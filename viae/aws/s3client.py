from flask import json
import boto3
import constants.constants as c
import datetime as dt 
import os
import re

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


def upload_fileobj(fbytes, bucket, fname):
    s3client.upload_fileobj(fbytes, bucket, fname, ExtraArgs={'ACL':'public-read'})
# downloads state.json from s3, reads current image id, and increments, rewrites to file and uploads to s3

def move_to_validate_data(typ, filename):
    s3 = boto3.resource('s3')
    
    copy_source = {
        'Bucket': f'{const.s3_bucket}',
        'Key': f'image-annotations/in-progress/{typ}/{filename}'
    }

    s3.meta.client.copy_object(
            ACL='public-read',
            Bucket=f'{const.s3_bucket}',
            CopySource=copy_source,
            Key=f'image-annotations/validate-data/{typ}/{filename}'
    )

    s3.meta.client.delete_object(
        Bucket=f'{const.s3_bucket}',
        Key=f'image-annotations/in-progress/{typ}/{filename}'
    )

def move_to_destination(typ, filename, destination):
    s3 = boto3.resource('s3')
    
    copy_source = {
        'Bucket': f'{const.s3_bucket}',
        'Key': f'image-annotations/in-progress/{typ}/{filename}'
    }

    s3.meta.client.copy_object(
            ACL='public-read',
            Bucket=f'{const.s3_bucket}',
            CopySource=copy_source,
            Key=f'image-annotations/{destination}/{typ}/{filename}'
    )

    s3.meta.client.delete_object(
        Bucket=f'{const.s3_bucket}',
        Key=f'image-annotations/in-progress/{typ}/{filename}'
    )