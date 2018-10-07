# S3 bucket and folders
S3_STEM = 'https://s3.amazonaws.com/'
BUCKET = 'viae-image-annotator'

# this is where in progess labeling data are stored
IN_PROGRESS = f'{S3_STEM}{BUCKET}/in_progress_data/'
IN_PROGRESS_IMAGES = f'{IN_PROGRESS}images/'
IN_PROGRESS_COCO = f'{IN_PROGRESS}coco/'

# this is where completed labeling data are stored
VALIDATED = f'{S3_STEM}{BUCKET}/validated_data/'
VALIDATED_IMAGES = f'{VALIDATED}images/'
VALIDATED_COCO = f'{VALIDATED}coco/'

# store temp files
tmp = 'viae/tmp_files/'






