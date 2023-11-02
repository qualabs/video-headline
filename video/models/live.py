import sys
import time
import uuid

from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.db.models.signals import post_save, pre_delete, pre_save, post_delete
from django.dispatch import receiver
from django.utils import timezone
from django_fsm import FSMField, transition
from video.signals import cloudfront_deleted
from hub_auth.models import Account
from jsonfield import JSONField
from organization.models import Channel, Organization
from utils import cloudfront, medialive, cloudwatchevents, sns, cloudwatchlogs
from . import Tag


class LiveVideo(models.Model):
    '''
    Constants to represent the state`s of the Streaming
    '''

    class State:
        OFF = 'off'
        ON = 'on'
        STARTING = 'starting'
        STOPPING = 'stopping'
        WAITING_INPUT = 'waiting_input'
        DELETING = 'deleting'

        CHOICES = ((OFF, OFF), (ON, ON), (STARTING, STARTING), (STOPPING, STOPPING))

    class GeoType:
        WHITELIST = 'whitelist'
        BLACKLIST = 'blacklist'
        NONE = 'none'

        CHOICES = ((WHITELIST, WHITELIST), (BLACKLIST, BLACKLIST), (NONE, NONE))

    AUTOPLAY_CHOICES = (('c', 'Channel'), ('y', 'Yes'), ('n', 'No'))

    video_id = models.CharField(
        max_length=36,
        default=uuid.uuid4,
        unique=True,
        db_index=True,
        verbose_name='Video ID',
    )

    name = models.CharField(max_length=254, verbose_name='Name')

    created_by = models.ForeignKey(
        Account,
        models.SET_NULL,
        related_name='uploaded_live_video',
        verbose_name='Created by',
        null=True,
    )

    organization = models.ForeignKey(
        Organization,
        models.CASCADE,
        related_name='live_videos',
        verbose_name='Organization',
    )

    channel = models.ForeignKey(
        Channel,
        models.CASCADE,
        null=True,
        blank=True,
        related_name='live_videos',
        verbose_name='Channel',
    )

    tags = models.ManyToManyField(
        Tag, related_name='live_videos', verbose_name='Tags', blank=True
    )

    state = FSMField(
        default=State.OFF,
        verbose_name='Live Video state',
        choices=State.CHOICES,
        protected=True,
    )

    input_state = ArrayField(
        models.CharField(max_length=255, default='', verbose_name='Origin state'),
        default=list,
        blank=True,
    )

    metadata = JSONField(
        max_length=500, blank=True, default=dict, verbose_name='Metadata'
    )

    ads_vast_url = models.URLField(
        blank=True, null=True, max_length=1024, verbose_name='VAST URL (ads)'
    )

    enable_ads = models.BooleanField(default=True, verbose_name='Enable Ads?')

    created_at = models.DateTimeField(
        editable=False, default=timezone.now, verbose_name='Created'
    )

    ml_input_url = models.CharField(
        max_length=254, editable=False, default='', verbose_name='Input Url'
    )

    ml_input_id = models.CharField(
        max_length=36, editable=False, default='', verbose_name='Input Id'
    )

    ml_channel_arn = models.CharField(
        max_length=254, editable=False, default='', verbose_name='Channel Arn'
    )

    sns_topic_arn = models.CharField(
        max_length=254, editable=False, default='', verbose_name='Topic Arn'
    )

    autoplay = models.CharField(
        max_length=1, default='c', choices=AUTOPLAY_CHOICES, verbose_name='Autoplay?'
    )

    cf_id = models.CharField(
        max_length=100, verbose_name='Cf_id', editable=False, default=''
    )

    cf_domain = models.CharField(
        max_length=100, verbose_name='Cf_domain', editable=False, default=''
    )

    geolocation_type = models.CharField(
        max_length=20,
        editable=True,
        choices=GeoType.CHOICES,
        default=GeoType.NONE,
        verbose_name='Geolocation Type',
    )

    geolocation_countries = ArrayField(
        models.CharField(
            max_length=2,
            editable=True,
            default='',
            verbose_name='Geolocation Countries',
        ),
        default=list,
        blank=True,
    )

    def __init__(self, *args, **kwargs):
        super(LiveVideo, self).__init__(*args, **kwargs)
        self._old_geolocation_type = self.geolocation_type
        self._old_geolocation_countries = self.geolocation_countries
        self._old_channel = self.channel

    def __str__(self):
        return f'{self.video_id} ({self.name})'

    def ml_channel_id(self):
        return self.ml_channel_arn.split(':')[-1]

    class Meta:
        verbose_name = 'Live Video'
        verbose_name_plural = 'Live Videos'

    @transition(field=state, source=[State.STOPPING], target=State.OFF)
    def _to_off(self):
        pass

    @transition(field=state, source=[State.STARTING], target=State.WAITING_INPUT)
    def _to_waiting(self):
        pass

    @transition(field=state, source=[State.WAITING_INPUT], target=State.ON)
    def _to_on(self):
        pass

    @transition(field=state, source=[State.STOPPING, State.OFF], target=State.STARTING)
    def _to_starting(self):
        pass

    @transition(
        field=state,
        source=[State.STARTING, State.ON, State.WAITING_INPUT],
        target=State.STOPPING,
    )
    def _to_stopping(self):
        pass

    @transition(field=state, source=[State.OFF], target=State.DELETING)
    def _to_deleting(self):
        pass

    def to_starting(self):
        self._to_starting()
        medialive.start_channel(self)
        self.save()

    def to_stopping(self):
        self._to_stopping()
        medialive.stop_channel(self)
        self.save()

    def to_waiting(self):
        self._to_waiting()
        cloudwatchlogs.check_input_state(self)
        self.save()

    def to_on(self):
        self._to_on()
        self.save()

    def to_off(self):
        self._to_off()
        self.input_state.clear()
        self.save()

    def to_deleting(self):
        self._to_deleting()
        self.save()
        channel_id = self.ml_channel_arn.split(':')[-1]
        account_id = self.organization.aws_account.account_id
        video_id = self.video_id
        try:
            medialive.delete_channel(channel_id, account_id)
        except medialive.ChannelNotFoundException:
            pass
        finally:
            medialive.delete_input(self.ml_input_id, account_id)
        cloudfront.update_distribution(self.organization, self.cf_id, False)
        cloudwatchevents.remove_targets(self)
        cloudwatchevents.delete_rule(self)
        sns.unsubscribe_all(self)
        sns.delete_topic(self)
        cloudfront._delete_cloudfront_distribution.delay(
            self.cf_id, account_id, video_id
        )


@receiver(pre_save, sender=LiveVideo, dispatch_uid='validate_save_fields')
def live_pre_save_receiver(sender, instance, **kwargs):
    instance.geolocation_countries = list(filter(None, instance.geolocation_countries))


@receiver(post_save, sender=LiveVideo, dispatch_uid='create_media_live_service')
def live_video_post_save_receiver(sender, instance, created, **kwargs):
    if 'test' in sys.argv:
        return

    if created:
        # Create input
        input = medialive.create_input(instance)
        channel = medialive.create_channel(instance, input)

        instance.ml_input_id = input['Input']['Id']
        instance.ml_input_url = input['Input']['Destinations'][0]['Url']
        instance.ml_channel_arn = channel['Channel']['Arn']

        medialive.alert_service(instance)

        bucket_name = instance.organization.bucket_name

        """
                define custom settings for CloudFront creation
                  -id: origin id
                  -domain: S3 bucker domain
                  -target: origin Id
                  -caller: operation unique identificator (in this case integer timestamp)
        """

        cf_settings = {
            'id': bucket_name,
            'domain': f"{bucket_name}.s3.amazonaws.com",
            'path': f"/live/{instance.video_id}",
            'target': bucket_name,
            'caller': str(time.time()),
            'defaultTTL': 5,
            'maxTTL': 10,
        }
        new_distribution = cloudfront.create_distribution(
            cf_settings, instance.organization, instance.channel
        )

        instance.cf_id = new_distribution['cf_id']
        instance.cf_domain = new_distribution['cf_domain']

        instance.save()

    # Executed only if geoblocking options are updated
    elif (
        instance._old_geolocation_type != instance.geolocation_type
        or instance._old_geolocation_countries != instance.geolocation_countries
    ):
        cloudfront.update_distribution_geoblocking(
            instance.cf_id,
            instance.geolocation_type,
            instance.geolocation_countries,
            instance.organization,
        )

    # Executed only if channel is updated
    elif instance._old_channel and instance._old_channel.id != instance.channel.id:
        cloudfront.tag_distribution(
            instance.organization,
            instance.cf_id,
            [('vh:channel-id', str(instance.channel.id))],
        )


@receiver(cloudfront_deleted)
def handle_cloudfront_deleted(sender, video_id, **kwargs):
    try:
        live = LiveVideo.objects.get(video_id=video_id)
        live.delete()
    except live.DoesNotExist:
        pass  # Handle the case where the object doesn't exist
