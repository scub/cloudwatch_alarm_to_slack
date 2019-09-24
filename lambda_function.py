#!/usr/bin/env python3

import json, os

import requests

def lambda_handler(event, context):

    # Webhook fed in via Lambda Environment variable
    WEBHOOK = os.environ['SLACK_HOOK']
    event_content = event['Records'][0]

    if event_content['EventSource'] == 'aws:sns':

        status_code = 'No event sent - Failed'
        payload = dict()

        if 'Message' in event_content['Sns']:

            MESSAGE = json.loads(event_content['Sns']['Message'])

            try:
                payload['attachments'] = [{
                    'fallback': MESSAGE['AlarmName'],
                    'title': MESSAGE['AlarmDescription'],
                    'text': MESSAGE['NewStateReason']
                }]

                try:
                    print("Processing alarm trigger")
                    trigger = MESSAGE['Trigger']
                    info = "Namespace: {0} || Metric: {1} on {2} {3}".format(
                        trigger['Namespace'],
                        trigger['MetricName'],
                        trigger['Dimensions'][0]['name'],
                        trigger['Dimensions'][0]['value'])


                except Exception as UnknownDefinition:
                    print("Unable to find alarm trigger: {}".format(str(UnknownDefinition)))
                    info = None

                try:
                    print("Adding color")
                    if MESSAGE['NewStateValue'] == 'ALARM':
                        color = '#e60000'
                    else:
                        color = '#36a64f'

                    payload['attachments'][0].update({'color': color})
                except Exception as FailedToAddColor:
                    print("Failed to add color: {}".format(str(FailedToAddColor)))


                print("Adding author attachment if applicable")
                if info is not None:
                    print("Author attachment was applicable")
                    payload['attachments'][0].update({
                        'author': info
                    })

                print("Checking for a subject")
                if 'Subject' in event_content['Sns']:
                    print("We have one, adding it to the payload")
                    payload['attachments'][0].update({
                        'pretext': event_content['Sns']['Subject']
                    })
            except Exception as LikelyTestMessage:
                print( "WE FAILED HARD: {}".format(LikelyTestMessage) )
                message = "{0}{1}".format(
                    '' if 'Subject' not in event_content['Sns'] else "{}: ".format(event_content['Sns']['Subject']),
                    '' if 'Message' not in event_content['Sns'] else "{}".format(event_content['Sns']['Message'])
                )

                payload = {
                    "text": message
                }


        if WEBHOOK:
            req = requests.post(
                # Webhook received from environment
                WEBHOOK,
                # Content headers
                headers = {
                    'Content-Type': 'application/json'
                },
                # Payload consists of our sns Subject and Message
                data = json.dumps(payload)
            )

            print(json.dumps(payload))

            status_code = req.status_code

        return {
            'statusCode': 200,
            'body': json.dumps("Sent the following to slack: {}\nHook: {}\nResponse: {}".format( json.dumps(payload), WEBHOOK, status_code ))

        }

    return {
        'statusCode': 500,
        'body': json.dumps('Unable to process incompatible EventSource!')
    }



if __name__ == '__main__':

    event = {
        "Records": [{
            "EventSource": "aws:sns",
            "EventVersion": "1.0",
            "EventSubscriptionArn": "arn:aws:sns:us-east-1:765783612490:cloudwatch_slack_relay:9ed7f134-29e7-4cc7-ab99-ca85b4cce7ca",
            "Sns": {
                "Type": "Notification",
                "MessageId": "1de85e4a-6da7-5978-839b-084ee05a3796",
                "TopicArn": "arn:aws:sns:us-east-1:765783612490:cloudwatch_slack_relay",
                "Subject": 'ALARM: "RDS: svc-ca-backend-prod High Connections" in US East (N. Virginia)',
                "Message": "{\"AlarmName\":\"RDS: svc-ca-backend-prod High Connections\",\"AlarmDescription\":\"svc-ca-backend-prod is considered to have a high number of connections\",\"AWSAccountId\":\"765783612490\",\"NewStateValue\":\"ALARM\",\"NewStateReason\":\"Threshold Crossed: 1 out of the last 1 datapoints [75.0 (24/09/19 21:32:00)] was greater than the threshold (25.0) (minimum 1 datapoint for OK -> ALARM transition).\",\"StateChangeTime\":\"2019-09-24T21:33:49.363+0000\",\"Region\":\"US East (N. Virginia)\",\"OldStateValue\":\"OK\",\"Trigger\":{\"MetricName\":\"DatabaseConnections\",\"Namespace\":\"AWS/RDS\",\"StatisticType\":\"Statistic\",\"Statistic\":\"AVERAGE\",\"Unit\":null,\"Dimensions\":[{\"value\":\"svc-ca-backend-prod-cluster\",\"name\":\"DBClusterIdentifier\"}],\"Period\":60,\"EvaluationPeriods\":1,\"ComparisonOperator\":\"GreaterThanThreshold\",\"Threshold\":25.0,\"TreatMissingData\":\"- TreatMissingData:                    missing\",\"EvaluateLowSampleCountPercentile\":\"\"}}",
                "Timestamp": "2019-09-24T21:33:49.403Z",
                "SignatureVersion": "1",
                "Signature": "D4YGPLSkQqBhFtbeFztGMUqZHX0v33D0YgHxrnjHs5/LZqe83xMBX4eCh9XsAhf8hatHG7MJzw3rx+y/EMj5KKoF1y1omSoUinpkOzgwB/4RJl+/27luUX7Tzk0bj+LguULVr/A1jRaZALM6OHV/0Ml82Zzu3Ya624IKezgos5RoC1sz2g6iTbCrmbuYHutT+r9MPTF8GOZrBFHfUGqO4Ahmf713157fNgzbxqT1r2gP9vK4T/a4vZtEK56DIPOtKtanLzS6s2mwZK3Zl51ebxrW6mR+4Eu8Qvifz/hStXZkKpJdPBiOhB37Spe1ekVMg8m+rLXT3NQWxvmly+UdLA==",
                "SigningCertUrl": "https://sns.us-east-1.amazonaws.com/SimpleNotificationService-6aad65c2f9911b05cd53efda11f913f9.pem",
                "UnsubscribeUrl": "https://sns.us-east-1.amazonaws.com/?Action=Unsubscribe&SubscriptionArn=arn:aws:sns:us-east-1:765783612490:cloudwatch_slack_relay:9ed7f134-29e7-4cc7-ab99-ca85b4cce7ca",
                "MessageAttributes": {}
            }
        }]
    }

    #print(json.loads(event['Records'][0]['Sns']['Message']))

    lambda_handler( event, None )
