import json
import boto3
from boto3.dynamodb.conditions import Key

def lambda_handler(event, context):
    path_parameters = event.get('pathParameters', {})
    id = path_parameters.get('id')
    dynamodb = boto3.resource('dynamodb')
    dynamo_table = path_parameters.get('table')
    table = dynamodb.Table(dynamo_table) 

    if id is not None:
            try :
                table_response = table.query(
                    KeyConditionExpression=Key('ScheduleId').eq(id)
                )
                items = table_response.get('Items', [])  
                if items:
                    response = {
                        'status_code': 200,
                        'body':{
                            'message': 'Item found successfully',
                            'data': json.loads(json.dumps(items))
                        }
                    }
                    return response
                else:
                    response = {
                        'status_code': 404,
                        'body':{
                            'message': 'Item not found',
                            'data': []
                        }
                    }
                    raise Exception(response)
            except boto3.exceptions.ClientError as e:
        # Handle specific DynamoDB errors
                error_code = e.response['Error']['Code']
                if error_code == 'ResourceNotFoundException':
                    response = {
                        'status_code': 404,
                        'body':{
                            'message': 'Item not found',
                            'data': []
                        }
                    }
                else :
                    response = {
                        'status_code': 500,
                        'body':{
                            'message': 'Internal server error',
                            'data': []
                        }
                    }
                raise Exception(response)
    else:
        try:
            table_response = table.scan()
            items = table_response.get('Items', [])
            response = {
                'status_code': 200,
                'body':{
                    'message': 'Items found successfully',
                    'data': json.loads(json.dumps(items))
                }
            }
            return response
        except Exception as e:
            response = {
                'status_code': 500,
                'body':{
                    'message': 'Internal server error',
                    'data': []
                }
            }
            raise Exception(response)


