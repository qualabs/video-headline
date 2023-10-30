import json
import boto3
from boto3.dynamodb.conditions import Key


def lambda_handler(event, context):
    path_parameters = event.get('pathParameters', {})
    id = path_parameters.get('id')
    dynamodb = boto3.resource('dynamodb')
    dynamo_table = path_parameters.get('table')
    table = dynamodb.Table(dynamo_table) 
    response = {}

    if id is not None:
        try:
            table_response = table.query(
                KeyConditionExpression=Key('ScheduleId').eq(id)
            )
            items = table_response.get('Items', [])  
            if items:
                response["status_code"] = 200
                body = { "message" : "Item found succesfuly",
                        "data" : json.dumps(items)}
                response ["body"] = body
                
            else:
                response["status_code"] = 404 
                body = {"message" : "Item not found",
                        "data" : []}
                response["body"] = body
                
        except Exception as e:
            response["status_code"] = 500
            body  = {"message" : 'Internal server error',
                    "data" : []}
    else:
        try:
            table_response = table.scan()
            items = table_response.get('Items', [])
            response["status_code"] = 200
            body = {"message" : "Items found succesfuly",
                   "data" : json.dumps(items)}
            response["body"] = body

        except Exception as e:
            status_code = 500
            body = {"message" : "Internal server error",
                    "data" : [] }
            response["body"] = body


    return response