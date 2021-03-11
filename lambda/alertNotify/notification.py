import notificationConfig
from datetime import datetime

from linebot import LineBotApi
from linebot.exceptions import InvalidSignatureError, LineBotApiError
from linebot.models import TemplateSendMessage, CarouselTemplate, CarouselColumn, PostbackAction, TextSendMessage


class SourceColumn():
    def __init__(self, dataModel):
        self.imageUrl = dataModel['faceDetection']['s3']['sourceImageUrl']
        self.imageCaptureTime = datetime.fromtimestamp(int(dataModel['frame']['captureResult']['timestamp'] + 28800))
        
class MemberColumns():
    def __init__(self, dataModel):
        self.matchedFaceList = dataModel['faceValidation']['validationResult']['matchedFaceList']

class MatchedFacesMessage():
    def __init__(self, sourceColumn, memberColumns):
        self.__sourceColumn = sourceColumn
        self.__memberColumns = memberColumns
     
    def __getSourceCarouselColumn(self):
        sourceCarouselColumn = CarouselColumn(
                                    thumbnail_image_url=self.__sourceColumn.imageUrl,
                                    title='來源影像',
                                    text='時間：{}'.format(self.__sourceColumn.imageCaptureTime),
                                    actions=[
                                        PostbackAction(
                                            label=' ',
                                            data='doNothing'
                                        )
                                    ]
                                )
        
        return sourceCarouselColumn
    
    def __getMemberCarouselColumns(self):
        memberCarouselColumns = []
        
        for memberFace in self.__memberColumns.matchedFaceList:
            carouselColumn = CarouselColumn(
                thumbnail_image_url=memberFace['targetUrl'],
                title='成員影像',
                text='相似度：{}%'.format(round(memberFace['similarity'], 2)),
                actions=[
                    PostbackAction(
                        label=' ',
                        data='doNothing'
                    )
                ]
            )
            
            memberCarouselColumns.append(carouselColumn)
        
        return memberCarouselColumns
    
    def getCarouselTemplate(self):
        sourceCarouselColumn = self.__getSourceCarouselColumn()
        memberCarouselColumns = self.__getMemberCarouselColumns()
        carouselTemplate = TemplateSendMessage(
                                alt_text='收到通報訊息！',
                                template=CarouselTemplate(
                                    columns=[sourceCarouselColumn] + memberCarouselColumns
                                )
                            )
        
        return carouselTemplate
        
class ValidationResultMessage():
    def __init__(self, dataModel):
        self.__matchedFaceResult = dataModel['matchingResult']
        self.__imageCaptureTime = datetime.fromtimestamp(int(dataModel['frame']['captureResult']['timestamp'] + 28800))
        self.__matchedFaceCount = dataModel['faceValidation']['validationResult']['memberFaceCount']
        self.__matchedFaceList = dataModel['faceValidation']['validationResult']['matchedFaceList']
        self.__faceDetectionCount = dataModel['faceDetection']['detectionResult']['faceCount']
        self.__faceDetectionList = dataModel['faceDetection']['detectionResult']['faceList']
        self.text = None
        
    def __getMatchedFaceListText(self):
        matchedFaceListText = '\t\t匹配數量：{}\n\n'.format(self.__matchedFaceCount)
        
        for index, memberFace in enumerate(self.__matchedFaceList, start=1):
            faceCoordinate = {
                                'X': round(memberFace['boundingBox']['Left'] + 0.5 * memberFace['boundingBox']['Width'], 2), 
                                'Y': round(memberFace['boundingBox']['Top'] + 0.5 * memberFace['boundingBox']['Height'], 2), 
                             }
            faceArea = round(memberFace['boundingBox']['Width'] * memberFace['boundingBox']['Height'], 5)
            faceSimilarity = round(memberFace['similarity'], 2)
            
            matchedFaceListText += '\t\t\t\t[{0}] 位置：({1[X]}, {1[Y]})\n' \
                                    '\t\t\t\t\t\t\t面積：{2}\n' \
                                    '\t\t\t\t\t\t\t相似度：{3}%\n\n'.format(index, faceCoordinate, faceArea, faceSimilarity)
        
        return matchedFaceListText
    
    def __getFaceDetectionListText(self):
        faceDetectionListText = '\t\t來源人臉數量：{}\n\n'.format(self.__faceDetectionCount)
        
        for index, face in enumerate(self.__faceDetectionList, start=1):
            faceCoordinate = {
                                'X': round(face['boundingBox']['Left'] + 0.5 * face['boundingBox']['Width'], 2), 
                                'Y': round(face['boundingBox']['Top'] + 0.5 * face['boundingBox']['Height'], 2), 
                             }
            faceArea = round(face['boundingBox']['Width'] * face['boundingBox']['Height'], 5)
            faceConfidence = round(face['confidence'], 2)
            
            faceDetectionListText += '\t\t\t\t[{0}] 位置：({1[X]}, {1[Y]})\n' \
                                    '\t\t\t\t\t\t\t面積：{2}\n' \
                                    '\t\t\t\t\t\t\t信心指數：{3}%\n\n'.format(index, faceCoordinate, faceArea, faceConfidence)
                                    
        return faceDetectionListText
    
    def getTextTemplate(self):
        matchedFaceListText = self.__getMatchedFaceListText()
        faceDetectionListText = self.__getFaceDetectionListText()
        self.text = '成員查驗\n\n' \
                    '\t\t結果：{0}\n' \
                    '\t\t時間：{1}\n\n' \
                    '{2}' \
                    '{3}'.format(self.__matchedFaceResult, self.__imageCaptureTime, matchedFaceListText, faceDetectionListText)
        
        textTemplate = TextSendMessage(text=self.text)
        
        return textTemplate

class AlertNotify():
    def __init__(self, matchedFacesMessage, validationResultMessage):
        self.__receiverLineId = notificationConfig.receiverLineId
        self.__matchedFacesMessage = matchedFacesMessage
        self.__validationResultMessage = validationResultMessage
     
    def pushMessages(self):
        matchedFacesTemplateMessage = self.__matchedFacesMessage.getCarouselTemplate()
        validationResulTemplateMessage = self.__validationResultMessage.getTextTemplate()
        
        lineBotApi = LineBotApi(notificationConfig.channelAccessToken)
        
        try:
            lineBotApi.push_message(self.__receiverLineId, [matchedFacesTemplateMessage, validationResulTemplateMessage])
            pushResult = 'Success'
            
        except LineBotApiError as e:
            pushResult = 'LineBotApiError: {}'.format(e.error.message)
        
        return pushResult