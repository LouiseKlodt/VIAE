VIAE is an extension of [VIA](http://www.robots.ox.ac.uk/~vgg/software/via/), a sophisticated open-source image annotation tool developed at the University of Oxford. VIA is a browser based application with no server side storage of image or labeling data. VIAE is extending and adapting VIA by providing a back-end and data transformation to standard [COCO](http://cocodataset.org/#format-data) format. The server is storing images and labeling data on a S3 location (configurable to your own bucket), allowing to resume work at a later stage. 


## Installation
Clone this repo and use pip3 to install the requirements.
```
$ pip3 install --upgrade -r requirements.txt 
```

## S3 bucket setup
VIAE uploads and retrieves labeling and image data from an S3 bucket. Follow these steps to set up VIAE to work with your S3 Bucket:
* Set the Bucket name to your Bucket's name in [aws_config.py](https://github.com/LouiseKlodt/viae/blob/master/viae/constants/aws_config.py). 
* Upload the `categories.json` and `state.json` files into your S3 bucket. Do NOT rename the files or store them in another folder within the Bucket. VIAE is looking for these file names in the top level of the bucket.

* If not already set up, configure your AWS security credentials, to be able to access S3 using VIAE. See https://docs.aws.amazon.com/general/latest/gr/aws-security-credentials.html.


## Usage
Once you've configured your AWS S3 bucket and credentials, Run the application from the root directory.
```
$ python3 viae
```

The application is now running on http://0.0.0.0:5000/

## Dev notes