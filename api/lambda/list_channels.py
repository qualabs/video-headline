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
            response = media_tailor.describe_channel(ChannelName=channel_id)
            channel_data = response.get('Channel', {})
            channel['CreationTime'] = json_serial(channel['CreationTime'])
            channel['LastModifiedTime'] = json_serial(channel['LastModifiedTime'])            
            return {
                'statusCode': 200,
                'body': json.dumps(channel_data, default=json_serial)
            }
        except media_tailor.exceptions.ClientError as e:
            return {
                'statusCode': 404,
                'body': json.dumps({'message': 'Channel not found'})
            }
    else:
        try:
            response = media_tailor.list_channels()
            channels_data = response.get('Items', [])
            channels_data = list(map(lambda channel: {**channel, 'CreationTime': json_serial(channel['CreationTime']), 'LastModifiedTime' : json_serial(channel['LastModifiedTime'])}, channels_data))


            return {
                'statusCode': 200,
                'body': json.dumps(channels_data, default=json_serial)
            }
        except media_tailor.exceptions.ClientError as e:
            return {
                'statusCode': 500,
                'body': json.dumps({'message': 'Internal Server Error'})
            }
