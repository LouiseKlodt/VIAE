# S3 bucket and folders
S3_STEM = 'https://s3.amazonaws.com/'
S3_BUCKET = 'viae_image_annotator' # replace with your bucket name

# this is where in progess labeling data are stored
S3_IN_PROGRESS = f'{S3_STEM}{S3_BUCKET}/in_progress_data/'
S3_IN_PROGRESS_IMAGES = f'{S3_IN_PROGRESS}images/'
S3_IN_PROGRESS_COCO = f'{S3_IN_PROGRESS}coco/'

# this is where completed labeling data are stored
S3_VALIDATED = f'{S3_STEM}{S3_BUCKET}/validated_data/'
S3_VALIDATED_IMAGES = f'{S3_VALIDATED}images/'
S3_VALIDATED_COCO = f'{S3_VALIDATED}coco/'

# store temp files
tmp = 'viae/tmp_files/'






