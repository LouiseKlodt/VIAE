import util.aws_config as conf

# -----------------------------------------------------
# not to be configured / generated autmatically by VIAE
IN_PROGRESS_FOLDER = 'in_progress_data'
VALIDATE_FOLDER = 'validate_data'

# this is where in progess labeling data are stored
IN_PROGRESS = f'{conf.S3_STEM}{conf.BUCKET}/in_progress_data/'
IN_PROGRESS_IMAGES = f'{IN_PROGRESS}images/'
IN_PROGRESS_COCO = f'{IN_PROGRESS}coco/'

# this is where completed labeling data are stored
VALIDATED = f'{conf.S3_STEM}{conf.BUCKET}/validated_data/'
VALIDATED_IMAGES = f'{VALIDATED}images/'
VALIDATED_COCO = f'{VALIDATED}coco/'

PROGRESS_COCO = 'in_progress_data/coco/'
PROGRESS_IMAGES = 'in_progress_data/images/'

# store temp files
tmp = 'viae/tmp/'






