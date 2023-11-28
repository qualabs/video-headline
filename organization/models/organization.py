import sys
from django.db import models, IntegrityError
from django.db.models.signals import pre_save, post_save, pre_delete
from django.dispatch import receiver

from jsonfield import JSONField
from organization.models import AWSAccount
from organization.models.plan import Plan
from utils import s3


class Organization(models.Model):
    """ Organization is the top most level entity """

    name = models.CharField(max_length=100,
                            unique=True,
                            verbose_name='Name')
    contact_email = models.CharField(max_length=254,
                                     default='',
                                     blank=True,
                                     verbose_name='Contact Email')
    bucket_name = models.CharField(max_length=100,
                                   editable=False,
                                   default='',
                                   verbose_name='Bucket')
    cf_id = models.CharField(max_length=100,
                             editable=False,
                             default='',
                             verbose_name='Cf_id')
    cf_domain = models.CharField(max_length=100,
                                 editable=False,
                                 default='',
                                 verbose_name='Cf_domain')
    plan = models.ForeignKey(Plan,
                             models.PROTECT,
                             null=True,
                             default=None,
                             related_name='organizations',
                             verbose_name='Plan')
    config = JSONField(blank=True,
                       default=dict,
                       verbose_name='Configuration')
    aws_account = models.ForeignKey(AWSAccount,
                                    null=True,
                                    related_name='organizations',
                                    on_delete=models.PROTECT,
                                    verbose_name='AWS_account')
    upload_enabled = models.BooleanField(
        default=True,
        verbose_name='Enabled to upload videos'
    )
    traffic_enabled = models.BooleanField(
        default=True,
        verbose_name='Data traffic enabled'
    )
    security_enabled = models.BooleanField(
        default=False,
        verbose_name='URL security enabled'
    )

    def __str__(self):
        return self.name

    @property
    def cf_distribution_ids(self):
        dists = list(self.channels.values_list('cf_id', flat=True))
        dists += list(self.live_videos.values_list('cf_id', flat=True))

        if self.cf_id:
            dists.append(self.cf_id)

        return dists

    class Meta:
        verbose_name = 'Organization'
        verbose_name_plural = 'Organizations'


# -------------------------------- Organization signals handlers -------------------------------- #
@receiver(pre_save, sender=Organization, dispatch_uid='org_bucket_name')
def org_pre_save_receiver(sender, instance, **kwargs):
    """
    Get from services trusted AWS S3 bucket name for a new organization.
    """
    # assign trusted bucket name
    instance.bucket_name = s3.generate_bucket_name(instance.name)

    aws_account = instance.aws_account
    if instance.security_enabled and not aws_account.cf_private_key and not aws_account.cf_key_pair_id:
        raise IntegrityError(
            'You must especified cf_private_key and cf_key_pair_id in AWS Account.')


@receiver(post_save, sender=Organization, dispatch_uid='org_saved')
def org_post_save_receiver(sender, instance, created, **kwargs):
    """
    Create a new AWS S3 bucket after that a new organization is saved.
    """
    if 'test' in sys.argv:
        return

    if created:
        # Create a default channel
        from organization.models import Channel
        s3.create_bucket(instance)

        Channel.objects.create(organization=instance, name="Default")

    # Updating plan
    else:
        bill = instance.bills.all().order_by('-date').first()
        if bill:
            bill.plan = instance.plan
            bill.save()


@receiver(pre_delete, sender=Organization, dispatch_uid='org_deleted')
def org_pre_delete_receiver(sender, instance, **kwargs):
    """
    If Organization is deleted the associated AWS S3 bucket should be previously deleted too.
    """
    if 'test' in sys.argv:
        return
    s3.delete_bucket(instance)
