from django.db import models
from solo.models import SingletonModel
from jsonfield import JSONField
import json
import os


class Configuration(SingletonModel):
    slack_notifications_url = models.URLField(blank=True, null=True)
    cloud_front_configuration = JSONField(
        blank=True, default={}, verbose_name='CloudFront Configuration'
    )

    class Meta:
        verbose_name = 'Global Configuration'


class MediaConvertConfiguration(models.Model):
    name = models.CharField(
        max_length=100, verbose_name='Name', unique=True, default='Default'
    )
    description = models.TextField(
        max_length=100, verbose_name='Description', null=True
    )
    settings = JSONField(
        blank=True,
        verbose_name='MediaConvert Configuration',
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'MediaConvert Configuration'
        verbose_name_plural = 'MediaConvert Configurations'


class MediaLiveConfiguration(models.Model):
    name = models.CharField(
        max_length=100, verbose_name='Name', unique=True, default=''
    )

    description = models.TextField(
        max_length=100, verbose_name='description', null=True
    )

    source_settings = JSONField(
        blank=True,
        verbose_name='Source Settings',
    )

    destination_settings = JSONField(
        blank=True,
        verbose_name='Destination Settings',
    )

    encoder_settings = JSONField(
        blank=True,
        verbose_name='Encoder Settings',
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'MediaLive Configuration'
        verbose_name_plural = 'MediaLive Configurations'
