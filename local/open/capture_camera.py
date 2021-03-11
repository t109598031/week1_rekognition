import cv2
import time
import copy
import threading
import boto3
import json
import base64  
import awsconfig
import config
from API.captureAPI import Capture

frame = None

client = boto3.client('stepfunctions', aws_access_key_id=awsconfig.access_key, aws_secret_access_key=awsconfig.secret_access_key,region_name= awsconfig.region_name)

def stream():

    global frame
    streamPort = 0
    videoSource = cv2.VideoCapture(streamPort)

    while True:
        try:
            if videoSource.isOpened():
                ret, frame = videoSource.read()
                Height , Width = frame.shape[:2]
                scale = None
                if Height/640 > Width/960:
                    scale = Height/640
                else:
                    scale = Width/960
                frame = cv2.resize(frame, (int(Width/scale), int(Height/scale)), interpolation=cv2.INTER_CUBIC)
                cv2.imshow("CSI",frame)
                cv2.waitKey(1)
                if ret == False:
                    videoSource = cv2.VideoCapture(streamPort)
        except:
            print('Source video is unavailable! reconnecting ....')

    videoSource.release()


streamingThread = threading.Thread(target = stream,daemon=True)
streamingThread.start()

def main():
    global frame
    while True:
        time.sleep(config.timeset)

        if frame is not None:

            print("Streaming........")
            
            model  = Capture().Frame(frame)

            model["config"] = config.config

            response = client.start_execution(
               stateMachineArn = awsconfig.stepfunction_ARN,
               input = json.dumps(model)
            )


if __name__ == '__main__':

    main()
