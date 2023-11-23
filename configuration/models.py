from django.db import models
from solo.models import SingletonModel
from jsonfield import JSONField
import json
import os


def get_default_media_convert_configuration_settings():
    file_path = os.path.join(
        os.path.dirname(__file__),
        "./configuration.samples/media_convert_configuration.sample",
    )

    with open(file_path) as f:
        conf_cont = json.load(f)
        return conf_cont


def get_default_media_live_source_settings():
    file_path = os.path.join(
        os.path.dirname(__file__),
        "./configuration.samples/media_live_input_attachments.sample",
    )
    with open(file_path) as f:
        conf_cont = json.load(f)
        return conf_cont


def get_default_media_live_destinations_settings():
    file_path = os.path.join(
        os.path.dirname(__file__),
        "./configuration.samples/media_live_destinations.sample",
    )
    with open(file_path) as f:
        conf_cont = json.load(f)
        return conf_cont


def get_default_media_live_encoder_settings():
    file_path = os.path.join(
        os.path.dirname(__file__),
        "./configuration.samples/media_live_encoder_settings.sample",
    )
    with open(file_path) as f:
        conf_cont = json.load(f)
        return conf_cont


class Configuration(SingletonModel):
    slack_notifications_url = models.URLField(blank=True, null=True)
    cloud_front_configuration = JSONField(
        blank=True, default={}, verbose_name="CloudFront Configuration"
    )

    class Meta:
        verbose_name = "Global Configuration"


class MediaConvertConfiguration(models.Model):
    name = models.CharField(
        max_length=100, verbose_name="Name", unique=True, default="Default"
    )
    description = models.TextField(
        max_length=100, verbose_name="Description", null=True
    )
    settings = JSONField(
        blank=True,
        default=get_default_media_convert_configuration_settings,
        verbose_name="MediaConvert Configuration",
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "MediaConvert Configuration"
        verbose_name_plural = "MediaConvert Configurations"


class MediaLiveConfiguration(models.Model):
    name = models.CharField(
        max_length=100, verbose_name="Name", unique=True, default=""
    )

    description = models.TextField(
        max_length=100, verbose_name="description", null=True
    )

    source_settings = JSONField(
        blank=True,
        default=get_default_media_live_source_settings,
        verbose_name="Source Settings",
    )

    destination_settings = JSONField(
        blank=True,
        default=get_default_media_live_destinations_settings,
        verbose_name="Destination Settings",
    )

    encoder_settings = JSONField(
        blank=True,
        default=get_default_media_live_encoder_settings,
        verbose_name="Encoder Settings",
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "MediaLive Configuration"
        verbose_name_plural = "MediaLive Configurations"
