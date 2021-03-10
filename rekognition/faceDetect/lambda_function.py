import base64
import boto3
import config
from faceDetect import FaceDetection


def lambda_handler(event, context):
    dataModel = event
    faceDetection = FaceDetection(dataModel, config.aws_access_key_id, config.aws_secret_access_key, config.region_name)
    faceDetection.detectFace()
    faceDetection.storeImage(config.s3BucketName)
    
    return faceDetection.getModel()