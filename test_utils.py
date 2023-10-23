from django.utils import timezone
from datetime import date

from organization.models import Organization, Channel, Plan, Bill
from hub_auth.models import Account, APIKey
from video.models import Media, LiveVideo, LiveVideoCut, Tag


def create_organizations(name, org_quantity, bucket_name='', contact_email='', cf_id='',
                         cf_domain='', plan=None, config=None):
    organizations = []
    for number in range(1, org_quantity + 1):
        org = Organization.objects.create(
            name=f'{name} {number}',
            bucket_name=bucket_name,
            contact_email=contact_email,
            cf_id=cf_id,
            cf_domain=cf_domain,
            plan=plan,
            config=config if config else {}
        )

        organizations.append(org)

    return organizations


def create_user(username, password, organization):
    user = Account.objects.create_user(
        username=username,
        password=password,
        organization=organization,
        email=f'{username}@admin.com'
    )

    return user


def create_superuser(username, password, organization):
    su = Account.objects.create_superuser(
        username=username,
        password=password,
        organization=organization,
        email='admin@admin.com'
    )

    return su


def create_key(name, user):
    key = APIKey.objects.create(
        name=f'{name}',
        account=user,
    )

    return key


def create_channels(name, organization, quantity, allowed_domains=[],
                    ads_vast_url=None, detect_adblock=False, autoplay=False,
                    cf_domain='domain.cloudfront.com'):
    channels = []
    for number in range(1, quantity + 1):
        channel = Channel.objects.create(
            name=f'{name} {number}',
            organization=organization,
            allowed_domains=allowed_domains,
            ads_vast_url=ads_vast_url,
            detect_adblock=detect_adblock,
            autoplay=autoplay,
            cf_domain=f'{number}.{cf_domain}',
            cf_id=f'my_cf_id_{number}'
        )

        channels.append(channel)

    return channels


def create_videos(name, created_by, organization, quantity, state=Media.State.WAITING_FILE,
                  metadata=None, ads_vast_url=None, enable_ads=True, autoplay='c',
                  created_at=None, media_type='video'):
    videos = []
    for number in range(1, quantity + 1):
        video = create_video(name, created_by, organization, number, state, metadata, ads_vast_url,
                             enable_ads, autoplay, created_at, media_type)
        videos.append(video)

    return videos


def create_live_videos(name, created_by, organization, quantity, state=LiveVideo.State.OFF,
                       metadata=None, ads_vast_url=None, enable_ads=True, autoplay='c',
                       created_at=None, ml_channel_arn='', input_state=[]):
    lives = []
    for number in range(1, quantity + 1):
        live = create_live_video(name, created_by, organization, number, state, metadata,
                                 ads_vast_url,
                                 enable_ads, autoplay, created_at, ml_channel_arn, input_state)

        lives.append(live)

    return lives


def create_tags(name, organization, quantity):
    tags = []
    for number in range(1, quantity + 1):
        tag = Tag.objects.create(
            name=f'{name} {number}',
            organization=organization
        )

        tags.append(tag)

    return tags


def create_live_cut(live, initial_time, final_time, description='',
                    state=LiveVideoCut.State.SCHEDULED):
    return LiveVideoCut.objects.create(
        live=live,
        initial_time=initial_time,
        final_time=final_time,
        description=description,
        state=state
    )


def add_channel_to_video(channel, video):
    video.channel = channel
    video.save()


def add_channel_to_live_video(channel, live):
    live.channel = channel
    live.save()


def create_video(name, created_by, organization, number, state=Media.State.WAITING_FILE,
                 metadata=None, ads_vast_url=None, enable_ads=True, autoplay='c',
                 created_at=None, media_type='video'):
    video = Media.objects.create(
        name=f'{name} {number}',
        created_by=created_by,
        organization=organization,
        state=state,
        metadata=metadata if metadata else {},
        ads_vast_url=ads_vast_url,
        enable_ads=enable_ads,
        autoplay=autoplay,
        created_at=created_at if created_at else timezone.now(),
        media_type=media_type
    )

    return video


def create_live_video(name, created_by, organization, number, state=LiveVideo.State.OFF,
                      metadata=None, ads_vast_url=None, enable_ads=True, autoplay='c',
                      created_at=None, ml_channel_arn='', input_state=[]):
    live = LiveVideo.objects.create(
        name=f'{name} {number}',
        created_by=created_by,
        organization=organization,
        state=state,
        metadata=metadata if metadata else {},
        ads_vast_url=ads_vast_url,
        enable_ads=enable_ads,
        autoplay=autoplay,
        created_at=created_at if created_at else timezone.now(),
        ml_channel_arn=ml_channel_arn,
        input_state=input_state
    )

    return live


def create_plans(name, quantity, description='', storage=0, video_transcoding=0, audio_transcoding=0, data_transfer=0):
    plans = []
    for number in range(1, quantity + 1):
        plan = Plan.objects.create(
            name=f'{name} {number}',
            description=description,
            storage=storage,
            video_transcoding=video_transcoding,
            audio_transcoding=audio_transcoding,
            data_transfer=data_transfer
        )

        plans.append(plan)

    return plans


def create_bill(organization, plan, month=date.today().replace(day=1), storage=0, video_transcoding=0,
                data_transfer=0):
    bill = Bill.objects.create(
        organization=organization,
        plan=plan,
        date=month,
        storage=storage,
        video_transcoding=video_transcoding,
        data_transfer=data_transfer
    )

    return bill
