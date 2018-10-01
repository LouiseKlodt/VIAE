from flask import Flask
from flask import render_template, make_response, jsonify, request, json
from flask_cors import CORS, cross_origin
from io import BytesIO
#from lib_cerebro_py.aws.aws_s3_object import AwsS3Object
from urllib.parse import urlparse

import boto3
import constants.constants as const
import contextlib
import helpers.aws as aws
import helpers.coco as coco
import os
import re
import requests
import sys
import urllib
import ssl

import shutil
import tempfile


app = Flask(__name__)
#CORS(app, resources=r'/images/*')


@app.route("/internal/health_check")
def health_check():
    return "ok\n"


@app.route("/via-style.css")
def stylesheet():
   return app.send_static_file('hbc-via-style.css')


@app.route('/')
def index():
    return make_response(render_template('viae.html'))


# get all data from S3 in_progress / post new images to S3 in_progress
@app.route('/images/in_progress', methods=['GET', 'POST'])
def images_in_progress():
    if request.method == 'POST':
        is_url = request.args.get("url")
        if is_url == 'true':
            urls = json.loads(request.data)
            url_list = urls.split()
            files_with_coco = []
            for u in url_list:
                url = urllib.parse.unquote(u)
                print(url)
                if url.startswith('https'):
                    ctx = ssl.create_default_context()
                else:
                    ctx = None
                with contextlib.closing(urllib.request.urlopen(url, context=ctx)) as f:
                    f_bytes = f.read()
                img_id = aws.inc_img_id()
                file_stem = const.remove_prefix(url)
                fname = f'{img_id}-{file_stem}'
                img_url = f'{const.s3_progress_images}{fname}'
                img_s3 = AwsS3Object(img_url)
                img_s3.upload_file_object(BytesIO(f_bytes), extra_args={'ACL':'public-read'})
                urllib.request.urlcleanup()
                coco_obj = coco.upload_coco_to_s3(img_id, img_url, fname, sys.getsizeof(f_bytes))
                files_with_coco.append({'image_url': img_url, 'coco': coco_obj})
            return jsonify(files_with_coco)
        else:    
            files = request.files
            files_with_coco = []
            for i in range(len(files)):
                f = files[f'file_{i}']
                f_bytes = f.read()
                img_id = aws.inc_img_id()
                fname = f'{img_id}-{f.filename}'
                img_url = f'{const.s3_progress_images}{fname}'
                img_s3 = AwsS3Object(img_url)
                img_s3.upload_file_object(BytesIO(f_bytes), extra_args={'ACL':'public-read'})
                coco_obj = coco.upload_coco_to_s3(img_id, img_url, fname, sys.getsizeof(f_bytes))
                via_obj = coco.coco2via(coco_obj)
                files_with_coco.append({'image_url': img_url, 'coco': coco_obj})
            return jsonify(files_with_coco)
    # GET
    coco_s3_uris = AwsS3Object(const.s3_progress_coco).list_objects()
    coco_urls = []
    for coco_uri in coco_s3_uris[1:]:  # NB: first item is bucket folder
        coco_urls.append(f'{const.s3_stem}{coco_uri.uri[5:]}')
        
    via_annot_data = {}
    for url in coco_urls:
        with contextlib.closing(urllib.request.urlopen(url)) as coco_file:
            coco_bytes = coco_file.read()
        coco_obj = json.loads(coco_bytes)
        via_dict = coco.coco2via(coco_obj)
        fname = list(via_dict)[0]
        annot_data = via_dict.get(fname)
        via_annot_data[fname] = annot_data
    return jsonify(via_annot_data)


@app.route('/images/in_progress/<image_id>', methods=['PUT', 'POST'])
def submit_data(image_id):
    if request.method == 'PUT': # save partial labeling data to s3 in_progress 
        via_label_data = json.loads(request.data)
        img_url = via_label_data['filename']
        fname = const.remove_prefix(img_url)
        coco_fname = const.to_json(fname)
        coco_obj = coco.via_to_coco(via_label_data, coco_fname)
        coco_s3 = AwsS3Object(f'{const.s3_progress_coco}{coco_fname}')
        coco_s3.upload_file(f'{const.tmp}{coco_fname}', extra_args={'ACL':'public-read'})
        os.remove(f'{const.tmp}{coco_fname}')

        via_annot_data = {}
        via_dict = coco.coco2via(coco_obj)
        fname = list(via_dict)[0]
        annot_data = via_dict.get(fname)
        via_annot_data[fname] = annot_data
        return jsonify(via_annot_data)

    # POST: move labeling data to s3 validate_data
    via_label_data = json.loads(request.data)
    img_url = via_label_data['filename']
    destination = via_label_data['destination']

    img_fname = const.remove_prefix(img_url)
    coco_fname = const.to_json(img_fname)
    coco_obj = coco.via_to_coco(via_label_data, coco_fname)

    progress_img_s3 = AwsS3Object(f'{const.s3_progress_images}{img_fname}')
    progress_coco_s3 = AwsS3Object(f'{const.s3_progress_coco}{coco_fname}')
    progress_coco_s3.upload_file(f'{const.tmp}{coco_fname}', extra_args={'ACL':'public-read'})
    os.remove(f'{const.tmp}{coco_fname}')

    aws.move_to_destination('coco', coco_fname, destination)
    aws.move_to_destination('images', img_fname, destination)

    via_annot_data = {}
    via_dict = coco.coco2via(coco_obj)
    fname = list(via_dict)[0]
    annot_data = via_dict.get(fname)
    via_annot_data[fname] = annot_data
    return jsonify(via_annot_data)


@app.route('/images/in_progress/<image_id>', methods=['DELETE'])
def delete_data(image_id):
    img_url = json.loads(request.data)
    # delete coco and image from in progress
    img_fname = const.remove_prefix(img_url)
    coco_fname = const.to_json(img_fname)
    progress_img_s3 = AwsS3Object(f'{const.s3_progress_images}{img_fname}')
    progress_coco_s3 = AwsS3Object(f'{const.s3_progress_coco}{coco_fname}')
    progress_img_s3.delete()
    progress_coco_s3.delete()
    return jsonify({'image_url': img_url, 'coco': coco_fname}) # 204 OK ?

'''

if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)
