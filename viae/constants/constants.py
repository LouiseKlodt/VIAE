# S3 bucket and folders to be configured by user of the tool
S3_STEM = 'https://s3-eu-west-1.amazonaws.com/' # replace 
BUCKET = 'viae-image-annotator' # replace

# keep track of ids
STATE_JSON = 'state.json' # replace


# -----------------------------------------------------
# not to be configured / generated autmatically by VIAE
IN_PROGRESS_FOLDER = 'in_progress_data'
VALIDATE_FOLDER = 'validate_data'
# this is where in progess labeling data are stored
IN_PROGRESS = f'{S3_STEM}{BUCKET}/in_progress_data/'
IN_PROGRESS_IMAGES = f'{IN_PROGRESS}images/'
IN_PROGRESS_COCO = f'{IN_PROGRESS}coco/'


# this is where completed labeling data are stored
VALIDATED = f'{S3_STEM}{BUCKET}/validated_data/'
VALIDATED_IMAGES = f'{VALIDATED}images/'
VALIDATED_COCO = f'{VALIDATED}coco/'

PROGRESS_COCO = 'in_progress_data/coco/'
PROGRESS_IMAGES = 'in_progress_data/images/'

# store temp files
tmp = 'viae/tmp/'






