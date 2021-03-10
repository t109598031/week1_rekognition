import json
import copy
import numpy as np
import cv2
import base64

def image_splite(frame,boundingboxes):
    imagelist = []
    image = np.fromstring(frame,np.uint8)
    image = cv2.imdecode(image,cv2.IMREAD_COLOR)
    size = image.shape
    height , width = size[0],size[1]
    for BBox in boundingboxes:
        upperLeftPointX = int(BBox['Left']*width)
        upperLeftPointY = int(BBox['Top']*height)               
        lowerRightPointX = int((BBox['Left']+BBox['Width'])*width)
        lowerRightPointY = int((BBox['Top']+BBox['Height'])*height)
        
        cut_image = copy.deepcopy(image)[upperLeftPointY:lowerRightPointY,upperLeftPointX:lowerRightPointX]

        cut_image = base64.b64encode(cv2.imencode('.jpg', cut_image)[1]).decode() 
        cut_image = base64.b64decode(cut_image)

        imagelist.append(cut_image) 

    print(len(imagelist))
    return imagelist