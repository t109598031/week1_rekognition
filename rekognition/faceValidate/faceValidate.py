import boto3
import base64
from cutImage import image_splite

class FaceValidation:
    def __init__(self, dataModel, aws_access_key_id, aws_secret_access_key, region_name, collection_id):
        self.__dataModel = dataModel
        self.__aws_access_key_id = aws_access_key_id
        self.__aws_secret_access_key = aws_secret_access_key
        self.__region_name = region_name
        self.__collection_id = collection_id
        print(dataModel)
    def faceValidate(self, memberUrlList, memberIdList):
        client = boto3.client('rekognition',aws_access_key_id =  self.__aws_access_key_id,aws_secret_access_key = self.__aws_secret_access_key, region_name = self.__region_name)
        threshold = self.__dataModel["config"]["threshold"]
        image_binary = base64.b64decode(self.__dataModel["frame"]["OpenCV"]["imageBase64"])
        matchingCount = 0
        matchingFaceList = []
        
        if self.__dataModel["faceDetection"]["detectionResult"]["faceCount"] == 1:
            
            self.__response=client.search_faces_by_image(CollectionId=self.__collection_id,
                                    Image={'Bytes':image_binary},
                                    FaceMatchThreshold=threshold,
                                    MaxFaces=10)
            matchingCount = len(self.__response["FaceMatches"])
            print(self.__response)
            if matchingCount !=0:
                
                matchingFaceList.append({
                    "faceId": self.__response["FaceMatches"][0]["Face"]["FaceId"],
                    "similarity":self.__response["FaceMatches"][0]["Similarity"],
                    "targetUrl": memberUrlList[self.__response["FaceMatches"][0]["Face"]["FaceId"]],
                    "boundingBox": self.__response["FaceMatches"][0]["Face"]["BoundingBox"],
                    # "boundingBox": self.__response["SearchedFaceBoundingBox"],
                    "targetId":memberIdList[self.__response["FaceMatches"][0]["Face"]["FaceId"]]
                })
            
        else:
            faceBoundingBox = []
            for face in self.__dataModel["faceDetection"]["detectionResult"]["faceList"]:
                faceBoundingBox.append(face["boundingBox"])
            faceImageList = image_splite(image_binary,faceBoundingBox)
            # faceBoundingBoxIndex = 0
            for faceImage in faceImageList:
                
                response=client.search_faces_by_image(CollectionId=self.__collection_id,
                                    Image={'Bytes':faceImage},
                                    FaceMatchThreshold=threshold,
                                    MaxFaces=10)
                
                matchingCount = matchingCount + len(response["FaceMatches"])
                if len(response["FaceMatches"]) !=0:
                    # print("YAAA: ", response["FaceMatches"][0]["Face"]["FaceId"])
                    matchingFaceList.append({
                        "faceId": response["FaceMatches"][0]["Face"]["FaceId"],
                        "similarity":response["FaceMatches"][0]["Similarity"],
                        "targetUrl": memberUrlList[response["FaceMatches"][0]["Face"]["FaceId"]],
                        "targetId":memberIdList[response["FaceMatches"][0]["Face"]["FaceId"]],
                        "boundingBox": response["FaceMatches"][0]["Face"]["BoundingBox"],
                        # "boundingBox": faceBoundingBox[faceBoundingBoxIndex]
                    })
                # faceBoundingBoxIndex = faceBoundingBoxIndex + 1
        validationResult = {
            "memberFaceCount":matchingCount,
            "matchedFaceList": matchingFaceList,
            "notMemberCount": self.__dataModel["faceDetection"]["detectionResult"]["faceCount"] - matchingCount
        }
        self.__dataModel["faceValidation"] = {}
        self.__dataModel["faceValidation"]["validationResult"] = validationResult
        
        if self.__dataModel["faceValidation"]["validationResult"]["memberFaceCount"]>0:
            self.__dataModel["matchingResult"]="成功"
        else :
            self.__dataModel["matchingResult"]="失敗"
        if self.__dataModel["faceValidation"]["validationResult"]["memberFaceCount"]<self.__dataModel["faceDetection"]["detectionResult"]["faceCount"]:
            self.__dataModel["result"] = "含非成員"
        else:
            self.__dataModel["result"] = "皆為成員"
        
        self.__dataModel["frame"]["OpenCV"]["imageBase64"] = ""
            
    def getModel(self):
        return self.__dataModel