VIAE is an extension of [VIA](http://www.robots.ox.ac.uk/~vgg/software/via/), a sophisticated open-source image annotation tool developed at the University of Oxford. VIA is a browser based application with no server side storage of image or labeling data. VIAE is extending and adapting VIA by providing a back-end and data transformation to standard [COCO](http://cocodataset.org/#format-data) format. The server is storing images and labeling data on a S3 location (configurable to your own bucket), allowing to resume work at a later stage. 

## Prerequisites
You need to have your AWS security credentials configured. 

## Installation
Clone this repo and use pip3 to install the requirements.
```
$ pip3 install --upgrade -r requirements.txt 
```

## Usage
Run the application from the root directory.
```
$ python3 viae
```

The application is now running on http://0.0.0.0:5000/

## Dev notes