from notification import SourceColumn, MemberColumns, MatchedFacesMessage, ValidationResultMessage, AlertNotify


def lambda_handler(event, context):
    dataModel = event
    dataModel['alertNotify'] = {'notificationResult': {}}
    
    # declare classes
    sourceColumn = SourceColumn(dataModel)
    memberColumns = MemberColumns(dataModel)
    matchedFacesMessage = MatchedFacesMessage(sourceColumn, memberColumns)
    validationResultMessage = ValidationResultMessage(dataModel)
    alertNotify = AlertNotify(matchedFacesMessage, validationResultMessage)
    
    # send messages to receiver
    pushResult = alertNotify.pushMessages()
    
    # put alertNotify logs into dataModel
    dataModel['alertNotify']['notificationResult']['linePushText'] = validationResultMessage.text
    dataModel['alertNotify']['notificationResult']['linePushResult'] = pushResult
    
    print(pushResult)
    
    return dataModel