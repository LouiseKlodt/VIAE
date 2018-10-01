from flask import json
#from lib_cerebro_py.aws.aws_s3_object import AwsS3Object

import boto3
import constants.constants as const
import datetime as dt 
import os
import re

'''
import botocore


s3 = boto3.resource('s3')

try:
    s3.Bucket(BUCKET_NAME).download_file(KEY, 'my_local_image.jpg')
except botocore.exceptions.ClientError as e:
    if e.response['Error']['Code'] == "404":
        print("The object does not exist.")
    else:
        raise
'''

def download_state_ids(via_state_s3):
    via_state_s3.download_file(f'{const.tmp}via_state.json')
    state_file = open(f'{const.tmp}via_state.json').read()
    state_data = json.loads(state_file)
    return state_data


# downloads state.json from s3, reads current image id, and increments, rewrites to file and uploads to s3
def inc_img_id():
    via_state_s3 = AwsS3Object(f'{const.s3_in_progress}via_state.json')
    state_data = download_state_ids(via_state_s3)

    last_img_id_zeroes = state_data['last_image_id']
    last_img_id = int(re.sub("^0+","", last_img_id_zeroes))
    new_img_id = str(1 + last_img_id)
    new_img_id_zeroes = new_img_id.zfill(5)
    state_data['last_image_id'] = new_img_id_zeroes

    with open(f'{const.tmp}via_state.json', 'w+') as new_state_file:
        new_state_file.write(json.dumps(state_data))
    new_state_file.close()

    via_state_s3.upload_file(f'{const.tmp}via_state.json', extra_args={'ACL':'public-read'})
    os.remove(f'{const.tmp}via_state.json')

    return new_img_id_zeroes


def inc_annot_id():
    via_state_s3 = AwsS3Object(f'{const.s3_in_progress}via_state.json')
    state_data = download_state_ids(via_state_s3)

    last_annotation_id_zeroes = state_data['last_annotation_id']
    last_annotation_id = int(re.sub("^0+","", last_annotation_id_zeroes))
    new_annotation_id = 1 + last_annotation_id
    new_annotation_id_zeroes = str(new_annotation_id).zfill(5)
    state_data['last_annotation_id'] = new_annotation_id_zeroes

    with open(f'{const.tmp}via_state.json', 'w+') as new_state_file:
        new_state_file.write(json.dumps(state_data))
    new_state_file.close()

    via_state_s3.upload_file(f'{const.tmp}via_state.json', extra_args={'ACL':'public-read'})
    os.remove(f'{const.tmp}via_state.json')

    return new_annotation_id_zeroes



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