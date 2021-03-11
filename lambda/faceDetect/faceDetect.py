import boto3
import base64
import copy

class FaceDetection:
    def __init__(self, dataModel, aws_access_key_id, aws_secret_access_key, region_name):
        self.__dataModel = dataModel
        self.__aws_access_key_id = aws_access_key_id
        self.__aws_secret_access_key = aws_secret_access_key
        self.__region_name = region_name
    def detectFace(self):
        client = boto3.client('rekognition',aws_access_key_id = self.__aws_access_key_id,aws_secret_access_key = self.__aws_secret_access_key,region_name = self.__region_name)
        image = base64.b64decode(self.__dataModel["frame"]["OpenCV"]["imageBase64"])
        self.__response = client.detect_faces(Image={'Bytes': image})
        faceCount = len(self.__response["FaceDetails"])
        faceList = []
        emptyDict = {}
        for faceDetected in self.__response["FaceDetails"]:
            faceModel = copy.deepcopy(emptyDict)
            faceModel["confidence"] = faceDetected["Confidence"]
            
            landmarkModel = faceDetected["Landmarks"]
            # for landmark in faceDetected["Landmarks"]:
            #     if landmark["Type"] == "nose":
            #         landmarkModel["nose"] = str(landmark["X"])+", "+str(landmark["Y"])
            #         break
            faceModel["landmark"] = landmarkModel
            
            faceModel["boundingBox"] = {
                "Width":faceDetected["BoundingBox"]["Width"],
                "Height":faceDetected["BoundingBox"]["Height"],
                "Top":faceDetected["BoundingBox"]["Top"],
                "Left":faceDetected["BoundingBox"]["Left"]
            }
            faceList.append(faceModel)
        self.__dataModel["faceDetection"] = {}
        self.__dataModel["faceDetection"]["detectionResult"] = {
            "faceCount": faceCount,
            "faceList": faceList
        }
    def storeImage(self, bucketName):
        client = boto3.client('s3', aws_access_key_id=self.__aws_access_key_id, aws_secret_access_key=self.__aws_secret_access_key,region_name=self.__region_name)
        image = self.__dataModel['frame']["OpenCV"]["imageBase64"] #input
        image = base64.b64decode(image)
    
        fileName = self.__dataModel["frame"]["captureResult"]["id"]
        # bucketName ='jamesbucket20210209'
        client.put_object(ACL='public-read',Body=image, Bucket=bucketName, Key=fileName ,ContentEncoding='base64',ContentType='image/jpeg')
        self.__dataModel["faceDetection"]["s3"] = {}
        self.__dataModel["faceDetection"]["s3"]["sourceImageUrl"] = 'https://' + bucketName + '.s3-' + self.__region_name + '.amazonaws.com/' + fileName
        self.__dataModel["faceDetection"]["s3"]["s3BucketName"] = bucketName
    def getModel(self):
        return self.__dataModel