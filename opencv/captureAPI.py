import copy
import base64  
import cv2
import time

class Capture():
    def __init__(self):

        self.frame = {
            "frame":{
                "OpenCV":{
                    "imageBase64":None
                },
                "captureResult":{
                    "id":None, 
                    "timestamp":None
                }  
            }
        }   

    def Frame(self,image):

        if image is not None:

            Height , Width = image.shape[:2]

            scale = None

            if Height/640 > Width/960:
                scale = Height/640
            else:
                scale = Width/960

            timestamp = time.time()

            image = cv2.resize(image.copy(), (int(Width/scale), int(Height/scale)), interpolation=cv2.INTER_CUBIC)
            self.frame["frame"]["OpenCV"]["imageBase64"] = base64.b64encode(cv2.imencode('.jpg', image)[1]).decode() 
            self.frame["frame"]["captureResult"]["id"] = "image" + str(int(timestamp)) + '.jpg'
            self.frame["frame"]["captureResult"]["timestamp"] = timestamp

            return self.frame
