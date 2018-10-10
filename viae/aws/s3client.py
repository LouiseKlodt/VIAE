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

    s3.meta.client.download_file(c.BUCKET, 'in_progress_data/via_state.json', 'viae/tmp/state.json')
    old_state_file = open('viae/tmp/state.json').read()
    state_ids = json.loads(old_state_file)

    old_img_id = state_ids['last_image_id']
    old_img_id_int = int(re.sub("^0+","", old_img_id))
    new_img_id_int = 1 + old_img_id_int
    new_img_id = str(new_img_id_int).zfill(5)
    state_ids['last_image_id'] = new_img_id

    with open('viae/tmp/state.json', 'w+') as new_state_file:
        new_state_file.write(json.dumps(state_ids))
    new_state_file.close()
    s3.meta.client.upload_file('viae/tmp/state.json', c.BUCKET, 'in_progress_data/via_state.json', ExtraArgs={'ACL':'public-read'})
    os.remove('viae/tmp/state.json')
    return new_img_id


def upload_image(fbytes, bucket, fname):
    s3client.upload_fileobj(fbytes, bucket, f'in_progress_data/images/{fname}', ExtraArgs={'ACL':'public-read'})


def upload_coco(img_id, img_url, fname, file_size):
    coco_fname = regex.to_json(fname)
    coco_obj = coco.setup_coco(img_id, img_url, fname, coco_fname, file_size)
    s3.meta.client.upload_file(f'{c.tmp}{coco_fname}', c.BUCKET, f'in_progress_data/coco/{coco_fname}', ExtraArgs={'ACL':'public-read'})
    #coco_s3 = AwsS3Object(f'{constants.s3_progress_coco}{coco_fname}')
    #coco_s3.upload_file(f'{constants.tmp}{coco_fname}', extra_args={'ACL':'public-read'})
    os.remove(f'{c.tmp}{coco_fname}')
    return coco_obj


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


def move_to_validate_data(typ, filename):
    #s3 = boto3.resource('s3')
    
    copy_source = {
        'Bucket': f'{const.BUCKET}',
        'Key': f'in_progress_data/{typ}/{filename}'
    }

    s3.meta.client.copy_object(
            ACL='public-read',
            Bucket=f'{const.BUCKET}',
            CopySource=copy_source,
            Key=f'validated_data/{typ}/{filename}'
    )

    s3.meta.client.delete_object(
        Bucket=f'{const.BUCKET}',
        Key=f'in_progress_data/{typ}/{filename}'
    )

'''
def move_to_destination(typ, filename, destination):
    #s3 = boto3.resource('s3')
    
    copy_source = {
        'Bucket': f'{const.BUCKET}',
        'Key': f'in_progress_data/{typ}/{filename}'
    }

    s3.meta.client.copy_object(
            ACL='public-read',
            Bucket=f'{const.BUCKET}',
            CopySource=copy_source,
            Key=f'image-annotations/{destination}/{typ}/{filename}'
    )

    s3.meta.client.delete_object(
        Bucket=f'{const.BUCKET}',
        Key=f'image-annotations/in-progress/{typ}/{filename}'
    )
    '''