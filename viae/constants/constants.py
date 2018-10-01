#from lib_cerebro_py.aws.aws_s3_object import AwsS3Object
import re 


# S3 bucket and folders
S3_STEM = 'https://s3.amazonaws.com/'
S3_BUCKET = 'viae_image_annotator' # replace with your bucket name
#KEY = 'my_image_in_s3.jpg' # replace with your object key

# this is where in progess labeling data are stored
S3_IN_PROGRESS = f'{S3_STEM}{S3_BUCKET}/in_progress_data/'
S3_IN_PROGRESS_IMAGES = f'{S3_IN_PROGRESS}images/'
S3_IN_PROGRESS_COCO = f'{S3_IN_PROGRESS}coco/'

# this is where completed labeling data are stored
S3_VALIDATED = f'{S3_STEM}{S3_BUCKET}/validated_data/'
S3_VALIDATED_IMAGES = f'{S3_VALIDATED}images/'
S3_VALIDATED_COCO = f'{S3_VALIDATED}coco/'

'''
s3_train = f'{S3_STEM}{S3_BUCKET}/image-annotations/train-data/'
s3_train_images = f'{s3_train}images/'
s3_train_coco = f'{s3_train}coco/'

s3_test = f'{S3_STEM}{S3_BUCKET}/image-annotations/test-data/'
s3_test_images = f'{s3_train}images/'
s3_test_coco = f'{s3_train}coco/'
'''

# store temp files
tmp = 'viae/tmp_files/'


# regex
def remove_prefix(img_url):
    return re.sub(r'.*\/([^\/]+)',r"\1", img_url)

def to_json(file_name):
    return re.sub(r'(\.[^.]*)$', '.json', file_name)
    




