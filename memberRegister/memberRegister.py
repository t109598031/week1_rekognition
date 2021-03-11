import boto3
import cv2
import base64
import copy

client = boto3.client('rekognition',aws_access_key_id = '<aws_access_key_id>',aws_secret_access_key = '<aws_secret_access_key>',region_name = 'us-west-2')
collection_id = "Face_Detection"

def create_collection(collection_id):

    #Create a collection
    print('Creating collection:' + collection_id)
    response=client.create_collection(CollectionId=collection_id)
    print('Collection ARN: ' + response['CollectionArn'])
    print('Status code: ' + str(response['StatusCode']))
    print('Done...')

def list_collections():

    max_results=10

    #Display all the collections
    print('Displaying collections...')
    response=client.list_collections(MaxResults=max_results)
    collection_count=0
    done=False
    
    while done==False:
        collections=response['CollectionIds']

        for collection in collections:
            print (collection)
            collection_count+=1
        if 'NextToken' in response:
            nextToken=response['NextToken']
            response=client.list_collections(NextToken=nextToken,MaxResults=max_results)
            
        else:
            done=True

    return collection_count 

def delete_collection(collection_id):


    print('Attempting to delete collection ' + collection_id)
    status_code=0
    try:
        response=client.delete_collection(CollectionId=collection_id)
        status_code=response['StatusCode']
        
    except ClientError as e:
        if e.response['Error']['Code'] == 'ResourceNotFoundException':
            print ('The collection ' + collection_id + ' was not found ')
        else:
            print ('Error other than Not Found occurred: ' + e.response['Error']['Message'])
        status_code=e.response['ResponseMetadata']['HTTPStatusCode']
    return(status_code)

def create_face_data(imagePath, name): 
    image2 = cv2.imread(imagePath)  
    pic = cv2.resize(image2, (640, 360), interpolation=cv2.INTER_CUBIC)
    image = base64.b64encode(cv2.imencode('.jpg', pic)[1]).decode()
    image_binary = base64.b64decode(image)
    faceId = []
    response=client.index_faces(CollectionId=collection_id,
                                Image={'Bytes':image_binary},
                                ExternalImageId=name,
                                MaxFaces=1,
                                QualityFilter="AUTO",
                                DetectionAttributes=['ALL'])
    # response = client.index_faces(CollectionId=collection_id, Image={'S3Object':{'Bucket':"member-registration-images",'Name':"Frank.jpg"}})
    for faceRecord in response['FaceRecords']:
        faceId.append(faceRecord['Face']['FaceId'])
    
    print (faceId)
    return faceId

def list_face_data():
    maxResults=10
    faces_count=0
    emptyDict = {}
    faceDataList = []
    tokens=True
    response=client.list_faces(CollectionId=collection_id,
                                MaxResults=maxResults)
    while tokens:
        faces=response['Faces']
        for face in faces:
            # print (face)
            faceData = copy.deepcopy(emptyDict)
            faceData["faceId"] = face["FaceId"]
            faceData["name"] = face["ExternalImageId"]
            faceDataList.append(faceData)
            faces_count+=1
        if 'NextToken' in response:
            nextToken=response['NextToken']
            response=client.list_faces(CollectionId=collection_id,
                                        NextToken=nextToken,MaxResults=maxResults)
        else:
            tokens=False

    print(faceDataList)
    return faceDataList

def delete_face_data(faceId):
    faceIdList = [faceId]
    response=client.delete_faces(CollectionId=collection_id,
                              FaceIds=faceIdList)
    if len(response['DeletedFaces'])==0:
        successfully = 'fail'
    else:
        successfully = 'success'
   
    return sucessfully

def main():
    create_collection(collection_id)
    list_collections()
    # delete_collection(collection_id)

    # create_face_data("C:/Users/ALEX/Desktop/Sign-in/face_image/Duncan.jpg", "Duncan")
    # list_face_data()
    # delete_face_data()

if __name__ == "__main__":
    main()