from django.db import models

from configuration.models import (
    MediaConvertConfiguration,
    MediaLiveConfiguration,
)


def get_default_mediaconvert_configuration():
    return MediaConvertConfiguration.objects.get_or_create(
        name='Default Media Convert Configuration',
    )[0]


def get_default_medialive_configuration():
    return MediaLiveConfiguration.objects.get_or_create(
        name='Default Media Live Configuration',
    )[0]


class Plan(models.Model):
    name = models.CharField(
        max_length=100, unique=True, verbose_name='Business name'
    )
    description = models.TextField(
        default='', blank=True, null=True, verbose_name='Description'
    )
    video_transcoding = models.FloatField(
        default=0, verbose_name='Video Transcoding Minutes'
    )
    audio_transcoding = models.FloatField(
        default=0, verbose_name='Audio Transcoding Minutes'
    )
    storage = models.FloatField(default=0, verbose_name='Storage (GB)')
    data_transfer = models.FloatField(default=0, verbose_name='Traffic (GB)')
    video_transcode_configuration = models.ForeignKey(
        MediaConvertConfiguration,
        models.PROTECT,
        null=True,
        default=get_default_mediaconvert_configuration,
        verbose_name='Video transcoding configuration',
        related_name='video_transcode_config',
    )

    audio_transcode_configuration = models.ForeignKey(
        MediaConvertConfiguration,
        models.PROTECT,
        null=True,
        default=get_default_mediaconvert_configuration,
        verbose_name='Audio transcoding configuration',
        related_name='audio_transcode_config',
    )

    medialive_configuration = models.ForeignKey(
        MediaLiveConfiguration,
        models.PROTECT,
        null=True,
        default=get_default_medialive_configuration,
        verbose_name='MediaLive Configuration',
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Plan'
        verbose_name_plural = 'Plans'
