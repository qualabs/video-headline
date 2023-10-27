import json
import boto3
from boto3.dynamodb.conditions import Key


def lambda_handler(event, context):
    path_parameters = event.get('pathParameters', {})
    id = path_parameters.get('id')
    dynamodb = boto3.resource('dynamodb')
    dynamo_table = path_parameters.get('table')
    table = dynamodb.Table(dynamo_table) 

    if id:
        try:
            response = table.query(
                KeyConditionExpression=Key('ScheduleId').eq(id)
            )
            items = response.get('Items', [])  
            print(items)
            if items:
                return {
                    'statusCode': 200,
                    'body': json.dumps(items)
                }
            else:
                return {
                    'statusCode': 404,
                    'body': json.dumps({'message': 'Not found'})
                }
        except Exception as e:
            print(e)
            return {
                'statusCode': 500,
                'body': json.dumps({'message': 'Internal Server Error'})
            }
    else:
        try:
            response = table.scan()
            items = response.get('Items', [])
            return {
                'statusCode': 200,
                'body': json.dumps(items)
            }
        except Exception as e:
            return {
                'statusCode': 500,
                'body': json.dumps({'message': 'Internal Server Error'})
            }
