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
    response = {}
    
    if channel_id:
        try:
            response = media_tailor.describe_channel(ChannelName=channel_id)
            channel_data = response.get('Channel', {})
            channel_data['CreationTime'] = json_serial(channel_data['CreationTime'])
            channel_data['LastModifiedTime'] = json_serial(channel_data['LastModifiedTime']) 
            if channel_data :
                response = {
                    'status_code': 200,
                    'body' : { 'messsage' : 'Created succesfuly',
                                'data' : json.dump(channel_data, default=json_serial) 
                        
                    }
                }
                
                
            else :
                response = { 'status_code': 404,
                            'body' : {
                                'message': 'Channel not found',
                                'data' : []
                                }
                            }
                raise Exception(response)

                
        except media_tailor.exceptions.ClientError as e:
                response = { 'status_code': 404,
                            'body' : {
                                'message': 'Channel not found',
                                'data' : []
                                }
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
                    'message' : 'Channel retrieved succesfuly',
                    'data' : json.dumps(channels_data, default=json_serial)
                }
            }

        except media_tailor.exceptions.ClientError as e:
            response = {
                'status_code' : 500,
                'body' : {
                    'message' : 'Internal Server Error',
                    'data' : []
                }
            }


        return response