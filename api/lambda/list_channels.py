import json
import boto3
from datetime import datetime
from datetime import date

media_tailor = boto3.client('mediatailor')

def json_serial(obj):
    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    raise TypeError("Type not serializable")

def lambda_handler(event, context):
    path_parameters = event.get('pathParameters', {})
    channel_id = path_parameters.get('id', None)

    if channel_id:
        try:
            channel_data = media_tailor.describe_channel(ChannelName=channel_id)
            del channel_data["ResponseMetadata"]
            channel_data['CreationTime'] = json_serial(channel_data['CreationTime'])
            channel_data['LastModifiedTime'] = json_serial(channel_data['LastModifiedTime']) 
            response = {
                'status_code': 200,
                'body' :  { 'messsage' : 'Retrieved succesfuly',
                             'data' : json.loads(json.dumps(channel_data, default=json_serial))
                            }
            }
            return response
        except media_tailor.exceptions.ClientError as e:
                response = { 
                    'status_code': 404,
                    'body' : {'message': 'Channel not found',
                             'data' : [] }
                            }
                raise Exception(response)
    else:
        try:
            response = media_tailor.list_channels()
            channels_data = response.get('Items', [])
            channels_data = list(map(lambda channel: {**channel, 'CreationTime': json_serial(channel['CreationTime']), 'LastModifiedTime' : json_serial(channel['LastModifiedTime'])}, channels_data))
            
            response = {
                'status_code' : 200,
                'body' : {
                    'message' : 'Channels retrieved succesfuly',
                    'data' : json.loads(json.dumps(channels_data, default=json_serial))
                }
            }
            
            return response

        except media_tailor.exceptions.ClientError as e:
            response = {
                'status_code' : 500,
                'body' : {
                    'message' : 'Internal Server Error',
                    'data' : []
                }
            }
            raise Exception(response)


