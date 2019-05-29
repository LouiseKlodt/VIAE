from flask import json
from urllib.parse import urlparse

import boto3
import coco.coco as coco
import constants.constants as c
import constants.regex as regex
import datetime as dt 
import os
import re
import urllib


s3 = boto3.resource('s3')
s3client = boto3.client('s3')


def inc_image_id():
    s3.meta.client.download_file(c.BUCKET, f'{c.STATE_JSON}', 'viae/tmp/state.json')
    old_state_file = open('viae/tmp/state.json').read()
    state_ids = json.loads(old_state_file)
    old_img_id = state_ids['last_image_id']
    old_img_id_int = 0
    if old_img_id != "00000": 
        old_img_id_int = int(re.sub("^0+","", old_img_id))
    new_img_id_int = 1 + old_img_id_int
    new_img_id = str(new_img_id_int).zfill(5)
    state_ids['last_image_id'] = new_img_id
    with open('viae/tmp/state.json', 'w+') as new_state_file:
        new_state_file.write(json.dumps(state_ids))
    new_state_file.close()
    s3.meta.client.upload_file('viae/tmp/state.json', c.BUCKET, f'{c.STATE_JSON}', ExtraArgs={'ACL':'public-read'})
    os.remove('viae/tmp/state.json')
    return new_img_id


def inc_annot_id():
    s3.meta.client.download_file(c.BUCKET, f'{c.STATE_JSON}', 'viae/tmp/state.json')
    old_state_file = open('viae/tmp/state.json').read()
    state_ids = json.loads(old_state_file)
    old_annot_id = state_ids['last_annotation_id']
    old_annot_id_int = 0
    if old_annot_id != "00000": 
        old_annot_id_int = int(re.sub("^0+","", old_annot_id))
    new_annot_id_int = 1 + old_annot_id_int
    new_annot_id = str(new_annot_id_int).zfill(5)
    state_ids['last_annotation_id'] = new_annot_id
    with open('viae/tmp/state.json', 'w+') as new_state_file:
        new_state_file.write(json.dumps(state_ids))
    new_state_file.close()
    s3.meta.client.upload_file('viae/tmp/state.json', c.BUCKET, f'{c.STATE_JSON}', ExtraArgs={'ACL':'public-read'})
    os.remove('viae/tmp/state.json')
    return new_annot_id


def upload_image(fbytes, bucket, fname):
    s3client.upload_fileobj(fbytes, bucket, f'{c.PROGRESS_IMAGES}{fname}', ExtraArgs={'ACL':'public-read'})


def upload_coco(coco_fname):
    s3.meta.client.upload_file(f'{c.tmp}{coco_fname}', c.BUCKET, f'{c.PROGRESS_COCO}{coco_fname}', ExtraArgs={'ACL':'public-read'})
    os.remove(f'{c.tmp}{coco_fname}')


def upload_file(source, dest):
     s3.meta.client.upload_file(source, c.BUCKET, dest, ExtraArgs={'ACL':'public-read'})


def download_file(bucket, key, dest):
    s3.meta.client.download_file(bucket, key, dest)
    f = open(dest).read()
    obj = json.loads(f)
    os.remove(dest)
    return obj


def list_urls(bucket, prefix):
    data = s3client.list_objects(Bucket = bucket, Marker = prefix, Prefix = prefix)
    urls = []
    if 'Contents' in data: 
        contents = data['Contents']
        for i in contents:
            url = i['Key']
            parsed_url = urllib.parse.quote(url)
            urls.append(f'{c.S3_STEM}{bucket}/{parsed_url}')
    return urls


def move_to_destination(typ, filename, destination):
    copy_source = {
        'Bucket': f'{c.BUCKET}',
        'Key': f'{c.IN_PROGRESS_FOLDER}/{typ}/{filename}'
    }
    s3.meta.client.copy_object(
            ACL='public-read',
            Bucket=f'{c.BUCKET}',
            CopySource=copy_source,
            Key=f'{destination}/{typ}/{filename}'
    )
    s3.meta.client.delete_object(
        Bucket=f'{c.BUCKET}',
        Key=f'{c.IN_PROGRESS_FOLDER}/{typ}/{filename}'
    )
    

def delete_file(typ, fname):
    s3client.delete_object(
        Bucket= c.BUCKET, 
        Key=f'{c.IN_PROGRESS_FOLDER}/{typ}/{fname}'
    )