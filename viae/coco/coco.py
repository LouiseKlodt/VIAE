from flask import json
import datetime as dt 
import re
import constants.constants as constants
import os
import aws as aws


def setup_coco(image_id, image_url, file_name, fname_json, file_size):
    coco = {
        'info': None, 
        'images': [], 
        'annotations': [], 
        'licenses': [],
        'categories': []
    }

    coco['info'] = {
        'year': dt.datetime.now().year, 
        'version': None, 
        'description': None, 
        'contributor': None, 
        'url': None, 
        'date_created': dt.datetime.now().isoformat()
    }

    image_data = {
        'id': image_id,
        'width': None, 
        'height': None, 
        'file_name': file_name,
        'license': None, 
        'flickr_url': image_url, 
        'coco_url': image_url, 
        'date_captured': None,
        'size': file_size
    }

    coco['images'].append(image_data)

    licenses_data = {
        'id': None, 
        'name': None,
        'url': None
    }

    coco['licenses'].append(licenses_data)

    coco_output = f'{constants.tmp}{fname_json}'
    with open(coco_output, 'w+') as f:
        f.write(json.dumps(coco))

    return coco


def via_to_coco(via_label_data, coco_fname):
    coco_url = f'{constants.s3_progress_coco}{coco_fname}'
    coco_s3 = AwsS3Object(coco_url)
    coco_s3.download_file(f'{constants.tmp}{coco_fname}')
    coco_file = open(f'{constants.tmp}{coco_fname}').read()
    coco = json.loads(coco_file)

    categories_s3 = AwsS3Object(f'{constants.s3_in_progress}categories.json')
    categories_s3.download_file(f'{constants.tmp}categories.json')
    cat_file = open(f'{constants.tmp}categories.json').read()
    categories_s3 = json.loads(cat_file)
    os.remove(f'{constants.tmp}categories.json')

    annotations = []
    for region in via_label_data['regions']:
        segmentation = []
        if region['shape_attributes']['name'] == 'polygon' or region['shape_attributes']['name'] == 'polyline':
            for i in range(len(region['shape_attributes']['all_points_x'])):
                segmentation.append(region['shape_attributes']['all_points_x'][i])
                segmentation.append(region['shape_attributes']['all_points_y'][i])
        else:
            break # TODO handle other shapes (rect, etc.)

        images = coco['images']
        categories = coco['categories']

        cat_name = region['region_attributes']['label']
        cat_ls = list(filter(lambda cat: cat['name'] == cat_name, categories_s3))
        
        category = {
            'supercategory': None,
            'id': cat_ls[0]['id'],
            'name': cat_ls[0]['name']
        }

        categories.append(category)

        if 'annotation_id' in region:
            annot_id = region['annotation_id']
        else:
            annot_id = aws.inc_annot_id()
        
        annotation = {
            'id': annot_id,
            'image_id': images[0]['id'],
            'category_id': cat_ls[0]['id'],
            'segmentation': [segmentation],
            'area': None,
            'bbox': [],
            'iscrowd': None
        }

        annotations.append(annotation)

    coco['annotations'] = annotations
    coco['images'][0]['size'] = via_label_data['size']
    coco_output = f'{constants.tmp}{coco_fname}'
    with open(coco_output, 'w+') as f:
        f.write(json.dumps(coco))

    return coco


def coco2via(coco_obj):

    via_dict = {}

    via_annotation = {
        'filename': None, 
        'size': coco_obj['images'][0]['size'], 
        'regions': [],
        'file_attributes': None
    }

    via_annotation['filename'] = coco_obj['images'][0]['coco_url']

    annotations = coco_obj['annotations']
    categories = coco_obj['categories']
    for annot in annotations:
        region = {
            'shape_attributes': None,
            'region_attributes': None,
            'annotation_id': None
        }
        shape_attr = {
            'name': 'polygon', # TODO check how to revert shape info
            'all_points_x': [],
            'all_points_y': []
        }
        region_attr = {
            'label': None
        }

        annotation_id = annot['id']
        cat_id = annot['category_id']
        labels = [cat['name'] for cat in categories if cat['id'] == cat_id]
        region_attr['label'] = labels[0]

        if annot['segmentation'] != None:
            segmentation = annot['segmentation']
            for segment in segmentation:
                shape_attr['all_points_x'] = segment[0::2]
                shape_attr['all_points_y'] = segment[not 0::2]
    
        region['shape_attributes'] = shape_attr
        region['region_attributes'] = region_attr
        region['annotation_id'] = annotation_id

        via_annotation['regions'].append(region)

    via_dict[coco_obj['images'][0]['file_name']] = via_annotation
    return via_dict