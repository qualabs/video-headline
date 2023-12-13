from django.db import models

from fernet_fields import EncryptedCharField, EncryptedTextField


class AWSAccount(models.Model):
    REGION_CHOICES = (
        ('us-east-1', 'us-east-1'),
        ('us-east-2', 'us-east-2'),
        ('us-west-1', 'us-west-1'),
        ('us-west-2', 'us-west-2'),
        ('ap-east-1', 'ap-east-1'),
        ('ap-south-1', 'ap-south-1'),
        ('ap-northeast-2', 'ap-northeast-2'),
        ('ap-southeast-1', 'ap-southeast-1'),
        ('ap-southeast-2', 'ap-southeast-2'),
        ('ap-northeast-1', 'ap-northeast-1'),
        ('ca-central-1', 'ca-central-1'),
        ('eu-central-1', 'eu-central-1'),
        ('eu-west-1', 'eu-west-1'),
        ('eu-west-2', 'eu-west-2'),
        ('eu-west-3', 'eu-west-3'),
        ('eu-north-1', 'eu-north-1'),
        ('me-south-1', 'me-south-1'),
        ('sa-east-1', 'sa-east-1'),
    )

    name = models.CharField(max_length=254, verbose_name='Name', blank=True, null=True)

    access_key = models.CharField(max_length=254,
                                  verbose_name='Access Key')
    secret_access_key = EncryptedCharField(max_length=254,
                                           verbose_name='Secret Access Key')
    region = models.CharField(max_length=254, verbose_name='Region', choices=REGION_CHOICES)
    media_convert_role = models.CharField(max_length=254, verbose_name='MediaConvert Role')
    media_convert_endpoint_url = models.URLField(max_length=254,
                                                 verbose_name='MediaConvert Endpoint URL')
    media_live_role = models.CharField(max_length=254, verbose_name='MediaLive Role')
    account_id = models.CharField(max_length=64, verbose_name='Account Id', blank=False, null=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'AWS Account'
        verbose_name_plural = 'AWS Accounts'
