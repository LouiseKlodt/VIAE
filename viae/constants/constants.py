#from lib_cerebro_py.aws.aws_s3_object import AwsS3Object
import re 


# S3 constants
s3_stem = 'https://s3.amazonaws.com/'
s3_bucket = 'bauta'

s3_in_progress = f'{s3_stem}{s3_bucket}/image-annotations/in-progress/'
s3_progress_images = f'{s3_in_progress}images/'
s3_progress_coco = f'{s3_in_progress}coco/'

s3_validate = f'{s3_stem}{s3_bucket}/image-annotations/validate-data/'
s3_validate_images = f'{s3_validate}images/'
s3_validate_coco = f'{s3_validate}coco/'

s3_train = f'{s3_stem}{s3_bucket}/image-annotations/train-data/'
s3_train_images = f'{s3_train}images/'
s3_train_coco = f'{s3_train}coco/'

s3_test = f'{s3_stem}{s3_bucket}/image-annotations/test-data/'
s3_test_images = f'{s3_train}images/'
s3_test_coco = f'{s3_train}coco/'


# store temp files
tmp = 'via-app/tmp-files/'


# regex
def remove_prefix(img_url):
    return re.sub(r'.*\/([^\/]+)',r"\1", img_url)

def to_json(file_name):
    return re.sub(r'(\.[^.]*)$', '.json', file_name)
    




