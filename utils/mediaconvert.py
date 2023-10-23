import pdb
import os
from pdb import Pdb
import boto3
import logging
import math
from celery import shared_task

logger = logging.getLogger('defalut')


def get_media_convert(aws_account):
    """
    :return: media_convert object (boto3)
    """
    # TODO: Uncomment and use cache
    # session = boto3.session.Session()
    # mediaclient = session.client('mediaconvert')
    # response = mediaclient.describe_endpoints(
    #     MaxResults=1
    # )
    # media_convert = session.client(
    #     'mediaconvert',
    #     endpoint_url=response['Endpoints'][0]['Url'])

    if aws_account:
        media_convert = boto3.client(
            'mediaconvert', aws_access_key_id=aws_account.access_key,
            aws_secret_access_key=aws_account.secret_access_key,
            endpoint_url=aws_account.media_convert_endpoint_url,
            region_name=aws_account.region)
    else:
        media_convert = boto3.client(
            'mediaconvert',
            endpoint_url=(os.getenv('AWS_MEDIA_CONVERT_ENDPOINT'))
        )

    return media_convert


def transcode(media):
    """
    Transcode videos from S3 bucket.
    Transcoding configuration is retrieved from organization settings
    """
    # retrieve organization
    organization = media.organization

    media_convert = get_media_convert(organization.aws_account)

    # retrieve transcoding settings
    if media.media_type == 'audio':
        conf_cont = media.organization.plan.audio_transcode_configuration.settings
        conf_cont = set_audio_transcode_output_location(conf_cont, organization, media)

    else:
        conf_cont = media.organization.plan.video_transcode_configuration.settings
        conf_cont = set_video_transcode_output_location(conf_cont, organization, media)

    # create job
    job = media_convert.create_job(
        Role=organization.aws_account.media_convert_role,
        Settings=conf_cont
    )

    # get job reference and associated to target video
    job_id = job['Job']['Id']
    media.metadata['media_convert_job_id'] = job_id
    media.save()

    check_job_status.delay(media.video_id)


def set_video_transcode_output_location(conf_cont, organization, media):
    """
    Replace conf settings, supplied values (keys):

        - destination (video): transcoded video output location
        - destination (thumbs): generated thumbnails output location
        - file input: video path to transcode


    minimum set of target keys (from base node) in profile JSON config file:

        "OutputGroups": [{
            "OutputGroupSettings": {
                "HlsGroupSettings": {
                    "Destination": transcoded video output location
                }
            }
        },
        {
            "OutputGroupSettings": {
                "FileGroupSettings": {
                    "Destination": generated thumbnails output location
                }
            }
        }],

        "Inputs": [{
            "FileInput": video path to transcode
        }]


    See docs on [1]: https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/mediaconvert.html#MediaConvert.Client.create_job
                [2]: >> default profile configuration on /configuration/media_convert_configuration.sample
    """
    # set video and thumbnails output location
    for entry in conf_cont['OutputGroups']:

        # transcoded video location
        if entry['Name'] == 'Apple HLS':
            entry['OutputGroupSettings']['HlsGroupSettings'][
                'Destination'] = f's3://{organization.bucket_name}/{media.video_id}/hls/output'

        # generated thumbnails location
        elif entry['CustomName'] == 'Thumbs':
            entry['OutputGroupSettings']['FileGroupSettings'][
                'Destination'] = f's3://{organization.bucket_name}/{media.video_id}/thumbs/thumb'

    # set video path to transcode (currently first entry data)
    conf_cont['Inputs'][0][
        'FileInput'] = f's3://{organization.bucket_name}/{media.video_id}/input.mp4'

    return conf_cont


def set_audio_transcode_output_location(conf_cont, organization, media):
    # set audio output location
    for entry in conf_cont['OutputGroups']:

        # transcoded audio location
        if entry['Name'] == 'File Group':
            entry['OutputGroupSettings']['FileGroupSettings'][
                'Destination'] = f's3://{organization.bucket_name}/{media.video_id}/audio/output'

    # set audio path to transcode (currently first entry data)
    conf_cont['Inputs'][0][
        'FileInput'] = f's3://{organization.bucket_name}/{media.video_id}/input.mp4'

    return conf_cont


@shared_task
def check_job_status(video_id):
    """
    Check Media Convert job status.
    """
    from video.models import Media

    media = Media.objects.select_related('organization__aws_account').get(video_id=video_id)

    job_id = media.metadata.get('media_convert_job_id')

    if not job_id:
        return check_job_status.apply_async(args=(video_id,), countdown=10)

    media_convert = get_media_convert(media.organization.aws_account)
    try:
        # recover job and update video status
        job = media_convert.get_job(Id=job_id)['Job']
        status = job['Status']

        if status == 'PROGRESSING':
            if media.state == Media.State.QUEUED:
                media.to_processing()
            else:
                media.metadata['job_percent_complete'] = job.get('JobPercentComplete')
                media.save()

            return check_job_status.apply_async(args=(video_id,), countdown=5)

        if status == 'COMPLETE':
            media.to_finished()
            media.metadata.pop('job_percent_complete')

            media.duration = math.ceil(
                job['OutputGroupDetails'][0]['OutputDetails'][0]['DurationInMs'] / 1000)
            media.save()
            return

        if status == 'ERROR':
            media.to_processing_failed()
            return

        return check_job_status.apply_async(args=(video_id,), countdown=10)
    except Exception:
        check_job_status.retry()
