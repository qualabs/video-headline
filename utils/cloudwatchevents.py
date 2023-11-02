import boto3
import json


class EventsNotFoundException(Exception):
    def __init__(self, message=''):
        self.message = message


def get_cloudwatch_event(aws_account):
    if aws_account:
        events = boto3.client(
            'events',
            aws_access_key_id=aws_account.access_key,
            aws_secret_access_key=aws_account.secret_access_key,
            region_name=aws_account.region,
        )
    else:
        events = boto3.client('events')

    return events


def put_rule(live):
    events = get_cloudwatch_event(live.organization.aws_account)

    conf = {
        "source": ["aws.medialive"],
        "detail-type": ["MediaLive Channel Alert"],
        "resources": [live.ml_channel_arn],
    }

    response = events.put_rule(
        Name=str(live.video_id), EventPattern=json.dumps(conf), State='ENABLED'
    )

    return response


def delete_rule(live):
    events = get_cloudwatch_event(live.organization.aws_account)

    try:
        events.delete_rule(Name=str(live.video_id))
    except events.exceptions.ResourceNotFoundException:
        raise EventsNotFoundException()


def put_targets(live):
    events = get_cloudwatch_event(live.organization.aws_account)

    targets = [
        {'Id': str(live.id), 'Arn': live.sns_topic_arn, 'InputPath': '$.detail'},
    ]
    response = events.put_targets(Rule=str(live.video_id), Targets=targets)

    return response


def remove_targets(live):
    events = get_cloudwatch_event(live.organization.aws_account)

    try:
        response = events.remove_targets(Rule=str(live.video_id), Ids=[str(live.id)])
    except events.exceptions.ResourceNotFoundException:
        raise EventsNotFoundException()
