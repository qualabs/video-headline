from datetime import datetime, timedelta
import boto3
from celery import shared_task


def get_cloudwatch(aws_account):
    if aws_account:
        cloudwatch = boto3.client('logs', aws_access_key_id=aws_account.access_key,
                                  aws_secret_access_key=aws_account.secret_access_key,
                                  region_name=aws_account.region)
    else:
        cloudwatch = boto3.client('logs')

    return cloudwatch


def check_input_state(live):
    check_input.delay(live.video_id)


@shared_task
def check_input(video_id):
    from video.models import LiveVideo

    live = LiveVideo.objects.get(video_id=video_id)
    cloudwatch = get_cloudwatch(live.organization.aws_account)

    log_group_name = 'ElementalMediaLive'
    filter_pattern = 'Accepted RTMP connection'
    log_stream_name = live.ml_channel_arn.replace(":", "_") + "_0"
    end_time = int(round(datetime.now().timestamp() * 1000))
    start_time = int((datetime.now() - timedelta(seconds=10)).timestamp()) * 1000

    try:
        response = cloudwatch.filter_log_events(
            logGroupName=log_group_name,
            logStreamNames=[log_stream_name],
            filterPattern=filter_pattern,
            startTime=start_time,
            endTime=end_time
        )

        if len(response['events']) > 0:
            live.to_on()
        else:
            return check_input.apply_async(args=(video_id,), countdown=10)

    except Exception as e:
        check_input.retry(exc=e, countdown=10)
