import sys
import uuid
from django.db import models
from django.db.models.signals import pre_delete
from django.dispatch import receiver
from django.utils import timezone
from django_fsm import FSMField, transition

from hub_auth.models import Account
from jsonfield import JSONField
from organization.models import Channel, Organization
from utils import cloudfront, mediaconvert, s3
from . import Tag


class Media(models.Model):
    '''
    Constants to represent the `state`s of the Video
    '''

    class State:
        WAITING_FILE = 'waiting_file'
        QUEUING_FAILED = 'queuing_failed'
        QUEUED = 'queued'
        PROCESSING = 'processing'
        PROCESSING_FAILED = 'processing_failed'
        FINISHED = 'finished'
        NOT_FINISHED = 'not_finished'
        FAILED = 'failed'

        CHOICES = (
            (WAITING_FILE, WAITING_FILE),
            (QUEUING_FAILED, QUEUING_FAILED),
            (QUEUED, QUEUED),
            (PROCESSING, PROCESSING),
            (PROCESSING_FAILED, PROCESSING_FAILED),
            (FINISHED, FINISHED)
        )

    AUTOPLAY_CHOICES = (('c', 'Channel'), ('y', 'Yes'), ('n', 'No'))

    MEDIA_TYPE_CHOICES = (('audio', 'Audio'), ('video', 'Video'))
    
    

    video_id = models.CharField(max_length=36,
                                default=uuid.uuid4,
                                unique=True,
                                db_index=True,
                                verbose_name='Content ID')

    name = models.CharField(max_length=254,
                            verbose_name='Name')

    created_by = models.ForeignKey(Account,
                                   models.SET_NULL,
                                   related_name='uploaded_videos',
                                   verbose_name='Created by',
                                   null=True)

    organization = models.ForeignKey(Organization,
                                     models.CASCADE,
                                     related_name='media',
                                     verbose_name='Organization')

    channel = models.ForeignKey(Channel,
                                models.CASCADE,
                                null=True,
                                blank=True,
                                related_name='media',
                                verbose_name='Channel')

    tags = models.ManyToManyField(Tag,
                                  related_name='media',
                                  verbose_name='Tags',
                                  blank=True)
    
    protocol_type = models.CharField(
        max_length=5,
        default='hls',
        verbose_name='Protocol Type'
    )

    state = FSMField(default=State.WAITING_FILE,
                     verbose_name='Video State',
                     choices=State.CHOICES,
                     protected=True)

    metadata = JSONField(
        max_length=500, blank=True, default={},
        verbose_name='Metadata'
    )

    ads_vast_url = models.URLField(
        blank=True,
        null=True,
        max_length=1024,
        verbose_name='VAST URL (ads)'
    )

    enable_ads = models.BooleanField(
        default=True,
        verbose_name='Enable Ads?'
    )

    autoplay = models.CharField(
        max_length=1,
        default='c',
        choices=AUTOPLAY_CHOICES,
        verbose_name='Autoplay?'
    )

    created_at = models.DateTimeField(
        editable=False,
        default=timezone.now,
        verbose_name='Created'
    )

    media_type = models.CharField(
        max_length=5,
        default='video',
        choices=MEDIA_TYPE_CHOICES,
        verbose_name='Content Type'
    )


    has_thumbnail = models.BooleanField(
        default=False,
        verbose_name='Has custom thumbnail?'
    )
    
    protocol_type = models.CharField(
        max_length=5,
        default='hls',
        verbose_name='Protocol Type'
    )

    storage = models.BigIntegerField(default=0,
                                  verbose_name='Size in bytes')

    duration = models.IntegerField(default=0,
                                   verbose_name='Duration in seconds')

    def __str__(self):
        return f'{self.video_id} ({self.name})'

    class Meta:
        verbose_name = 'Content'
        verbose_name_plural = 'Contents'

    def get_urls(self):
        channel = self.channel

        # Hacky patch. Don't know how you'd get into this state!
        if channel is None:
            return "", "", ""
        
        media_url = ''

        # Default mime type for video
        
        poster_url = ''

        if self.media_type == 'video':
            if self.protocol_type == "hls":
                media_url = f'https://{channel.cf_domain}/{self.video_id}/hls/output.m3u8'
                mime_type = 'application/x-mpegURL'
            elif self.protocol_type == "dash":
                media_url = f'https://{channel.cf_domain}/{self.video_id}/dash/output.mpd'
                mime_type = 'application/dash+xml'
            poster_url = f'https://{channel.cf_domain}/{self.video_id}/thumbs/thumb_high.0000000.jpg'

        elif self.media_type == 'audio':
            media_url = f'https://{channel.cf_domain}/{self.video_id}/audio/output.mp4'
            mime_type = 'audio/mp4'

        thumb_path = 'thumb.jpg' if self.has_thumbnail else 'thumbs/thumb_high.0000000.jpg'
        poster_url = f'https://{channel.cf_domain}/{self.video_id}/{thumb_path}'

        return poster_url, media_url, mime_type

    @transition(field=state, source=State.WAITING_FILE, target=State.QUEUED)
    def _to_queued(self):
        pass

    @transition(field=state, source=State.WAITING_FILE, target=State.QUEUING_FAILED)
    def _to_queued_failed(self):
        pass

    @transition(field=state, source=State.QUEUED, target=State.PROCESSING)
    def _to_processing(self):
        pass

    @transition(field=state, source=State.PROCESSING, target=State.PROCESSING_FAILED)
    def _to_processing_failed(self):
        pass

    @transition(field=state, source=[State.PROCESSING, State.QUEUED], target=State.FINISHED)
    def _to_finished(self):
        pass

    @transition(field=state,
                source=[State.FINISHED, State.PROCESSING_FAILED, State.FAILED,
                        State.QUEUING_FAILED],
                target=State.QUEUED)
    def _re_process(self):
        pass

    def to_queued(self):
        self._to_queued()
        # send video to transcode
        mediaconvert.transcode(self)
        self.save()

    def to_queued_failed(self):
        self._to_queued_failed()
        self.save()

    def to_processing(self):
        self._to_processing()
        self.save()

    def to_processing_failed(self):
        self._to_processing_failed()
        self.save()

    def to_finished(self):
        self._to_finished()
        self.storage = s3.get_size(self.organization, self.organization.bucket_name, self.video_id)
        self.save()

    def re_process(self):
        self._re_process()
        self.metadata = {}

        # Delete files on S3
        s3.delete_object(self.organization.bucket_name, '{}/thumb'.format(self.video_id),
                         self.organization.aws_account)
        s3.delete_object(self.organization.bucket_name, '{}/hls'.format(self.video_id),
                         self.organization.aws_account)

        # Invalidate cache on CloudFront
        cloudfront.create_invalidation(self.organization, self.channel.cf_id, [
            '/{}/thumb/*'.format(self.video_id),
            '/{}/hls/*'.format(self.video_id)
        ])

        mediaconvert.transcode(self)
        self.save()


@receiver(pre_delete, sender=Media, dispatch_uid='org_bucket_name')
def video_pre_delete_receiver(sender, instance, **kwargs):
    if 'test' in sys.argv:
        return

    key = instance.video_id

    s3.delete_object(instance.organization.bucket_name, key, instance.organization.aws_account)
