import boto3
import re
from celery import shared_task
from django.conf import settings

from organization.models import AWSAccount, Organization
from utils import cloudwatchevents, sns
from utils.s3 import delete_object

CHANNEL_STATES_TO_DELETE = ["IDLE", "CREATE_FAILED"]
INPUT_STATES_TO_DELETE = ["DETACHED"]


class ChannelNotFoundException(Exception):
    def __init__(self, message=""):
        self.message = message


def get_media_live(aws_account):
    if aws_account:
        media_live = boto3.client(
            "medialive",
            aws_access_key_id=aws_account.access_key,
            aws_secret_access_key=aws_account.secret_access_key,
            region_name=aws_account.region,
        )
    else:
        media_live = boto3.client("medialive")

    return media_live


def create_input(live):
    media_live = get_media_live(live.organization.aws_account)
    response = media_live.create_input(
        Type="RTMP_PUSH",
        Name=f"{live.video_id}",
        InputSecurityGroups=[input_security_group(media_live)],
        Destinations=[{"StreamName": f"live/{(live.video_id)}"}],
    )

    return response


def create_channel(live, source):
    organization = live.organization

    media_live = get_media_live(organization.aws_account)
    # Get MediaLive video configuration
    conf = organization.plan.medialive_configuration

    conf.destination_settings["Settings"][0][
        "Url"
    ] = f"s3://{organization.bucket_name}/live/{live.video_id}/output"
    conf.destination_settings["Id"] = organization.bucket_name

    conf.source_settings["InputId"] = source["Input"]["Id"]

    conf.encoder_settings["OutputGroups"][0]["OutputGroupSettings"]["HlsGroupSettings"][
        "Destination"
    ]["DestinationRefId"] = organization.bucket_name

    response = media_live.create_channel(
        ChannelClass="SINGLE_PIPELINE",
        Destinations=[conf.destination_settings],
        InputAttachments=[conf.source_settings],
        EncoderSettings=conf.encoder_settings,
        Name=live.name,
        RoleArn=organization.aws_account.media_live_role,
        LogLevel="INFO",
    )

    return response


def input_security_group(media_live):
    try:
        response = media_live.list_input_security_groups()["InputSecurityGroups"]
        return response[0]["Id"]
    except Exception:
        response = media_live.create_input_security_group(
            WhitelistRules=[
                {"Cidr": "0.0.0.0/0"},
            ]
        )
        return response["SecurityGroup"]["Id"]


def start_channel(live):
    media_live = get_media_live(live.organization.aws_account)

    try:
        media_live.start_channel(ChannelId=live.ml_channel_id())
    except media_live.exceptions.NotFoundException:
        raise ChannelNotFoundException()
    check_live_state.delay(live.video_id)


def stop_channel(live):
    media_live = get_media_live(live.organization.aws_account)

    try:
        media_live.stop_channel(ChannelId=live.ml_channel_id())
    except media_live.exceptions.NotFoundException:
        raise ChannelNotFoundException()
    check_live_state.delay(live.video_id)


@shared_task
def delete_channels():
    from video.models import LiveVideo

    for account in AWSAccount.objects.all():
        media_live = get_media_live(account)

        all_channels = media_live.list_channels()
        all_channels = all_channels["Channels"]
        all_channels_stopped = list(
            filter(
                lambda channel_entry: channel_entry["State"]
                in CHANNEL_STATES_TO_DELETE,
                all_channels,
            )
        )

        # Id of all "stopped" channels
        all_channels_stopped = [channel["Arn"] for channel in all_channels_stopped]
        channels_used = LiveVideo.objects.filter(
            ml_channel_arn__in=all_channels_stopped
        ).values_list("ml_channel_arn", flat=True)
        channels_used = list(channels_used)

        for channel_arn in all_channels_stopped:
            if channel_arn not in channels_used:
                channel_id = channel_arn.split(":")[-1]
                _delete_channel.delay(channel_id, account.id)


def delete_channel(channel_id, account_id):
    aws_account = AWSAccount.objects.get(account_id=account_id)
    media_live = get_media_live(aws_account)
    try:
        media_live.delete_channel(ChannelId=channel_id)
        check_channel_status.delay(channel_id, account_id)
    except Exception as e:
        raise Exception("Error deleting channel")

@shared_task
def check_channel_status(channel_id, account_id):
    try:
        aws_account = AWSAccount.objects.get(account_id=account_id)
        media_live = get_media_live(aws_account)
        channel = media_live.describe_channel(ChannelId=channel_id)
        state = channel["State"]

        if state == "DELETED":
            # channel was deleted, continue with delete input
            return 
        else:
            # channel was not deleted, check status again
            return check_channel_status.apply_async(args=(channel_id, account_id), countdown=5)
    except Exception as e:
        check_channel_status.retry(exc=e)

@shared_task
def _delete_channel(channel_id, account_id):
    aws_account = AWSAccount.objects.get(pk=account_id)
    media_live = get_media_live(aws_account)
    try:
        media_live.delete_channel(ChannelId=channel_id)
    except Exception as e:
        _delete_channel.retry(exc=e)


@shared_task
def delete_inputs():
    for account in AWSAccount.objects.all():
        media_live = get_media_live(account)

        all_inputs = media_live.list_inputs()["Inputs"]
        all_inputs_detached = list(
            filter(
                lambda input_entry: input_entry["State"] in INPUT_STATES_TO_DELETE,
                all_inputs,
            )
        )
        all_inputs_detached = [input["Id"] for input in all_inputs_detached]

        for input_id in all_inputs_detached:
            _delete_input.delay(input_id, account.id)


def delete_input(input_id, account_id):
    media_live = get_media_live(AWSAccount.objects.get(account_id=account_id))
    try:
        media_live.delete_input(InputId=input_id)
    except Exception as e:
        raise Exception(f"Error deleting input ${input_id}")


@shared_task
def _delete_input(input_id, account_id):
    media_live = get_media_live(AWSAccount.objects.get(pk=account_id))
    try:
        media_live.delete_input(InputId=input_id)
    except Exception as e:
        _delete_input.retry(exc=e)


@shared_task
def check_live_state(video_id):
    from video.models import LiveVideo

    live = LiveVideo.objects.get(video_id=video_id)
    media_live = get_media_live(live.organization.aws_account)

    try:
        channel = media_live.describe_channel(ChannelId=live.ml_channel_id())
        state = channel["State"]

        if state == "RUNNING":
            live.to_waiting()
        elif state == "IDLE":
            _delete_channel_storage(channel)
            live.to_off()

        else:
            return check_live_state.apply_async(args=(video_id,), countdown=10)

    except Exception as e:
        check_live_state.retry(exc=e)


def _delete_channel_storage(channel):
    bucket_url = channel["Destinations"][0]["Settings"][0]["Url"]
    regex = r"s3:\/\/([^\/]*)\/(.*)\/output"
    bucket, key = re.match(regex, bucket_url).groups()
    aws_account = Organization.objects.get(bucket_name=bucket).aws_account
    delete_object(bucket, key, aws_account)


def add_channel_alert(message):
    _add_channel_alert.delay(message)


@shared_task
def _add_channel_alert(message):
    from video.models import LiveVideo

    live = LiveVideo.objects.filter(ml_channel_arn=message["channel_arn"]).first()

    if not live:
        return

    if (
        message["alarm_state"] == "SET"
        and message["alert_type"] not in live.input_state
    ):
        live.input_state.append(message["alert_type"])
    if (
        message["alarm_state"] == "CLEARED"
        and message["alert_type"] in live.input_state
    ):
        live.input_state.remove(message["alert_type"])
    live.save()


def alert_service(live):
    try:
        cloudwatchevents.put_rule(live)
        topic_arn = sns.create_topic(live)

        live.sns_topic_arn = topic_arn

        cloudwatchevents.put_targets(live)

        endpoint = f"{settings.BASE_URL}api/v1/live-videos/notify/"
        sns.subscribe(live, endpoint)
    except Exception as ex:
        print(f"Error: {ex}")
