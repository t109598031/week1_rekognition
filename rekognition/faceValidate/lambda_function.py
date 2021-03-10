from faceValidate import FaceValidation
from faceId import memberUrlList, memberIdList
import config

def lambda_handler(event, context):
    dataModel = event
    faceValidation = FaceValidation(dataModel, config.aws_access_key_id, config.aws_secret_access_key, config.region_name, config.collection_id)
    faceValidation.faceValidate(memberUrlList, memberIdList)
    
    return faceValidation.getModel()