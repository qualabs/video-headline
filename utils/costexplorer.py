import boto3
import requests

from celery import shared_task
from datetime import date, timedelta
from dateutil.relativedelta import relativedelta
from django.db.models import Sum, Count, Q
from django.utils import timezone


def update_bill(bill):
    if bill.is_current_bill():
        today = date.today()
        usage = get_usage(
            bill.organization.aws_account,
            bill.organization.id,
            bill.date,
            today + relativedelta(days=1),
        )
    else:
        usage = get_usage(
            bill.organization.aws_account,
            bill.organization.id,
            bill.date,
            bill.date + relativedelta(months=1),
        )

    bill.storage = round(usage.pop('storage'), 3)
    bill.video_transcoding = round(usage.pop('video_transcoding'), 3)
    bill.audio_transcoding = round(usage.pop('audio_transcoding'), 3)
    bill.data_transfer = round(sum(i for i, j in usage['traffic_per_day']), 3)
    bill.extras = usage

    bill.save()


def get_usage(aws_account, org_id, initial_date, final_date):
    from organization.models import Channel

    storage_total, storage_per_channel = get_storage(org_id)
    (
        video_transcoding_total,
        audio_transcoding_total,
        transcoding_per_channel,
    ) = get_transcoding(org_id, initial_date, final_date)
    ce_data_transfer = get_data_transfer(aws_account, org_id, initial_date, final_date)

    traffic_per_day = []
    usage_per_channel = dict()

    channel_traffic_per_day = {}

    traffic_date = initial_date
    while traffic_date < final_date:
        string_date = traffic_date.strftime("%Y-%m-%d")
        channel_traffic_per_day[string_date] = 0.0
        traffic_date = traffic_date + timedelta(days=1)

    for c in Channel.objects.filter(organization_id=org_id):
        usage_per_channel[c.id] = {
            'name': c.name,
            'storage': storage_per_channel.get(c.id, 0),
            'transcoding': transcoding_per_channel.get(c.id, {'audio': 0, 'video': 0}),
            'data_transfer': 0.0,
            'traffic_per_day': channel_traffic_per_day.copy(),
        }

    for time in ce_data_transfer['ResultsByTime']:
        day = time['TimePeriod']['Start']
        total_of_day = 0.0

        if time['Total']:
            total_of_day += round(float(time['Total']['UsageQuantity']['Amount']), 3)

        for group in time['Groups']:
            channel_id = group['Keys'][0].split('$')[-1]
            channel_total = round(float(group['Metrics']['UsageQuantity']['Amount']), 3)

            if channel_id and usage_per_channel.get(int(channel_id)):
                channel_id = int(channel_id)
                usage_per_channel[channel_id]['data_transfer'] += channel_total
                usage_per_channel[channel_id]['traffic_per_day'][day] = channel_total

            total_of_day += channel_total

        traffic_per_day.append([total_of_day, day])

    return {
        'storage': storage_total,
        'video_transcoding': video_transcoding_total,
        'audio_transcoding': audio_transcoding_total,
        'traffic_per_day': traffic_per_day,
        'usage_per_channel': usage_per_channel,
    }


def get_storage(organization_id):
    from video.models import Media

    storage_total = 0
    storage_per_channel = dict()

    storage = (
        Media.objects.filter(organization_id=organization_id)
        .values('channel_id')
        .order_by('channel_id')
        .annotate(storage=Sum('storage'))
    )
    for channel in storage:
        storage_total += channel['storage']
        storage_per_channel[channel['channel_id']] = round(
            channel['storage'] / 1024**3, 3
        )
    storage_total = round(storage_total / 1024**3, 3)
    return storage_total, storage_per_channel


def get_transcoding(organization_id, initial_date, final_date):
    from video.models import Media

    audio_transcoding_total = 0
    video_transcoding_total = 0
    transcoding_per_channel = dict()

    transcoding = (
        Media.objects.filter(
            organization_id=organization_id,
            created_at__date__range=(initial_date, final_date),
        )
        .values('channel_id')
        .order_by('channel_id')
        .annotate(
            video_transcoding=Sum('duration', filter=Q(media_type='video')),
            audio_transcoding=Sum('duration', filter=Q(media_type='audio')),
        )
    )

    for channel in transcoding:
        channel_audio_transcoding = channel['audio_transcoding'] or 0
        channel_video_transcoding = channel['video_transcoding'] or 0
        transcoding_per_channel[channel['channel_id']] = {
            'audio': round(channel_audio_transcoding / 60, 3),
            'video': round(channel_video_transcoding / 60, 3),
        }

        audio_transcoding_total += channel['audio_transcoding'] or 0

        video_transcoding_total += channel['video_transcoding'] or 0

    video_transcoding_total = round(video_transcoding_total / 60, 3)
    audio_transcoding_total = round(audio_transcoding_total / 60, 3)

    return video_transcoding_total, audio_transcoding_total, transcoding_per_channel


def get_cost_explorer(aws_account):
    cost_explorer = boto3.client(
        'ce',
        aws_access_key_id=aws_account.access_key,
        aws_secret_access_key=aws_account.secret_access_key,
        region_name=aws_account.region,
    )
    return cost_explorer


def get_data_transfer(aws_account, org_id, initial_date, final_date):
    cost_explorer = get_cost_explorer(aws_account)

    result_daily = cost_explorer.get_cost_and_usage(
        TimePeriod={'Start': f'{initial_date}', 'End': f'{final_date}'},
        Granularity='DAILY',
        Filter={
            'And': [
                {
                    'Dimensions': {
                        'Key': 'USAGE_TYPE',
                        'Values': [
                            'US-DataTransfer-Out-Bytes',
                            'CA-DataTransfer-Out-Bytes',
                            'EU-DataTransfer-Out-Bytes',
                            'SA-DataTransfer-Out-Bytes',
                        ],
                    }
                },
                {
                    'Dimensions': {
                        'Key': 'SERVICE',
                        'Values': [
                            'Amazon CloudFront',
                        ],
                    },
                },
            ],
        },
        Metrics=["UsageQuantity"],
        GroupBy=[{'Key': 'vh:channel-id', 'Type': 'TAG'}],
    )

    return result_daily


@shared_task
def bill_renewal():
    from organization.models import Bill, Organization

    for org in Organization.objects.all():
        bill = org.bills.all().order_by('-date').first()
        update_bill(bill)

        if org.config.get('report_usage_to_slack', False):
            notify_monthly_usage(bill)

        Bill.objects.create(organization=org, plan=org.plan, date=timezone.now().date())


def notify_monthly_usage(bill):
    from configuration.models import Configuration

    config = Configuration.get_solo()
    if config.slack_notifications_url:
        org = bill.organization
        date = bill.date.strftime('%B-%Y')
        msg = {
            'text': f'*Usage Report {date} for {org.name}*',
            'blocks': [
                {
                    'type': 'section',
                    'text': {
                        'type': 'mrkdwn',
                        'text': f'*Usage Report {date} for {org.name}*',
                    },
                },
                {
                    'type': 'section',
                    'fields': [
                        {
                            'type': 'mrkdwn',
                            'text': f'*Storage*\n{round(bill.storage/1024, 3)} TB',
                        },
                        {
                            'type': 'mrkdwn',
                            'text': f'*Minutes of Videos Uploaded*\n{bill.video_transcoding} min',
                        },
                        {
                            'type': 'mrkdwn',
                            'text': f'*Minutes of Audio Uploaded*\n{bill.audio_transcoding} min',
                        },
                        {
                            'type': 'mrkdwn',
                            'text': f'*Transferred Data*\n{round(bill.data_transfer/1024, 3)} TB',
                        },
                    ],
                },
            ],
        }

        requests.post(config.slack_notifications_url, json=msg)
