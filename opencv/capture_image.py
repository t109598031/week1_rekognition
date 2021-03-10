import os 
import cv2
import time
import copy
import boto3
import json
import base64  
import awsconfig
import config
from API.captureAPI import Capture
import argparse


client = boto3.client('stepfunctions', aws_access_key_id=awsconfig.access_key, aws_secret_access_key=awsconfig.secret_access_key,region_name= awsconfig.region_name)

def main(frame):

    if frame is not None:

        print("Uploading.......")
            
        model  = Capture().Frame(frame)

        model["config"] = config.config


        #print(json.dumps(flowModel))

        response = client.start_execution(
           stateMachineArn = awsconfig.stepfunction_ARN,
           input = json.dumps(model)
        )

        print(response)

def find_dir():
    pathlist = []

    path = os.getcwd()

    for fd in os.listdir(path):
        full_path=os.path.join(path,fd)
        if os.path.isfile(full_path):
            if full_path.endswith('.png') or full_path.endswith('.jpg') or full_path.endswith('.jpeg'):
                pathlist.append(fd)
    return pathlist

if __name__ == '__main__':

    typelist = ["jpg","png","jpeg"]    

    parser = argparse.ArgumentParser(description='2021AI_BIGDATA_Class02_Demo, Only accept 3 Type of Imagefile .jpg .jpeg .png')
    parser.print_help()

    print("\nStarted......\n")

    imagelist = find_dir()

    print("The image current you can use for Recognition:")

    print(imagelist,"\n")

    while True:
        frame = input("Please Enter the File Name: ")

        if  frame != None: 
            if (str(frame) not in imagelist):

                print("Warning! Image not found,Please Enter the correct filename.")
            else:
                if str(frame).split(".")[1] not in typelist:
                    print("Warning! Image filetype incorrect.")
                else:
                    image = cv2.imread(frame)
                    main(image)

        else:
            print("Warning! Image not found,Please Enter the correct filename.")
