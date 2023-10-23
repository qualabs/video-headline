from secrets import token_urlsafe

import sys
import time
from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver

from organization.models import Organization
from utils import cloudfront


def get_channel_id():
    """
    Generate unique default tokens for Channel.channel_id field.
    """
    return token_urlsafe(16)


class Channel(models.Model):
    """
    Channels is the second level of organization and contains videos.
    """
    channel_id = models.CharField(max_length=36, default=get_channel_id, unique=True,
                                  db_index=True,
                                  editable=False, verbose_name='channel_id')
    organization = models.ForeignKey(Organization, related_name='channels',
                                     on_delete=models.CASCADE,
                                     verbose_name='Organization')
    name = models.CharField(max_length=100, verbose_name='Name')
    allowed_domains = ArrayField(models.CharField(max_length=254), blank=True, null=True,
                                 verbose_name='Allowed domains', default=list)
    ads_vast_url = models.URLField(blank=True,
                                   null=True,
                                   max_length=1024,
                                   verbose_name='VAST URL (ads)')
    detect_adblock = models.BooleanField(default=False, verbose_name='Detect AdBlock?')
    autoplay = models.BooleanField(default=False, verbose_name='Autoplay?')
    cf_id = models.CharField(max_length=100,
                             editable=False,
                             default='',
                             verbose_name='Cf_id')
    cf_domain = models.CharField(max_length=100,
                                 editable=False,
                                 default='',
                                 verbose_name='Cf_domain')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Channel'
        verbose_name_plural = 'Channels'
        unique_together = ('organization', 'name')


# -------------------------------- Channel signals handlers -------------------------------- #
@receiver(post_save, sender=Channel, dispatch_uid='channel_saved')
def channel_post_save_receiver(sender, instance, created, **kwargs):
    """
    Create a new AWS Cloudfront distribution after that a new channel is saved.
    """
    if 'test' in sys.argv:
        return

    if created:
        """
        define custom settings for CloudFront creation
            -id: origin id
            -domain: S3 bucker domain
            -target: origin Id
            -caller: operation unique identificator (in this case integer timestamp)
        """

        cf_settings = {
            'id': instance.organization.bucket_name,
            'domain': f"{instance.organization.bucket_name}.s3.amazonaws.com",
            'target': instance.organization.bucket_name,
            'caller': str(time.time()),
        }

        # execute CF tasks only on creation
        # recover new distribution CloudFront Id & DomainName after creation
        new_distribution = cloudfront.create_distribution(cf_settings, instance.organization, instance)

        # update organization properties (check creation)
        instance.cf_id = new_distribution['cf_id']
        instance.cf_domain = new_distribution['cf_domain']
        instance.save()


@receiver(pre_delete, sender=Channel, dispatch_uid='channel_deleted')
def channel_pre_delete_receiver(sender, instance, **kwargs):
    """
    If Channel is deleted the associated AWS CloudFront should be disabled.
    """
    if 'test' in sys.argv:
        return

    # delete all cloudfront distributions
    cloudfront.update_distribution_status(instance.organization, instance.cf_id)
