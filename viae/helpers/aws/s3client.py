from flask import json
import boto3
import constants.constants as const
import datetime as dt 
import os
import re

s3 = boto3.resource('s3')

s3client = boto3.client('s3')

bucket_name = 'viae-image-annotator'


# downloads via_state.json from S3 and returns map of ids
def download_state():
    s3.meta.client.download_file(bucket_name, 'in_progress_data/via_state.json', './tmp/state.json')
    old_state_file = open('tmp/state.json').read()
    old_state_ids = json.loads(old_state_file)
    return old_state_ids


# uploads updated state.json to S3
def upload_state(new_state_ids):
    with open('tmp/state.json', 'w+') as new_state_file:
        new_state_file.write(json.dumps(new_state_ids))
    new_state_file.close()
    s3.meta.client.upload_file('/tmp/state.json', bucket_name, 'via_state.json')
    os.remove('tmp/state.json')


def inc_image_id():
    old_state_ids = download_state()

    old_img_id = old_state_ids['last_image_id']
    old_img_id_int = int(re.sub("^0+","", last_img_id_zeroes))
    new_img_id_int = 1 + last_img_id_int
    new_img_id = str(new_img_id_int).zfill(5)
    state_ids['last_image_id'] = new_img_id

    upload_state(state_ids)
    return new_img_id



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