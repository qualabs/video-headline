from django.contrib import admin, messages
from fernet_fields import EncryptedCharField
from django.forms import widgets

from utils import cloudfront
from organization.models import Organization, Channel, AWSAccount, Plan, Bill


def disable_organization_data_traffic(modeladmin, request, queryset):
    for org in queryset:
        update_organization_data_traffic(org, False)

def enable_organization_data_traffic(modeladmin, request, queryset):
    for org in queryset:
        update_organization_data_traffic(org, True)

def update_organization_data_traffic(org, status):
    # update organization distribution status if exists
    if org.cf_id:
        cloudfront.update_distribution_status(org, org.cf_id, status)

    # udpate channels distributions status
    cf_dist_channels = org.channels.all().values_list('cf_id', flat=True)
    for chan in cf_dist_channels:
        cloudfront.update_distribution_status(org, chan, status)

    # update live videos distributions status
    cf_dist_live = org.live_videos.all().values_list('cf_id', flat=True)
    for dist in cf_dist_live:
        cloudfront.update_distribution_status(org, dist, status)
    org.traffic_enabled = status
    org.save()


def enable_signed_url_security(modeladmin, request, queryset):
    # After applying the change to the channels, change this to do it for each channel
    for org in queryset:
        if not org.aws_account.cf_private_key and not org.aws_account.cf_key_pair_id:
            return messages.error(request,
                                  f'The organization {org.name} does not have a private key specified in its AWS account.')

        cf = cloudfront.get_cloudfront_client(org.aws_account)
        
        # Update organization distribution trusted signers if exists
        if org.cf_id:
            update_cf_config_with_trusted_signer(cf, org.cf_id, org.aws_account.account_id)

        # Udpate channels distributions status
        cf_dist_channels = org.channels.all().values_list('cf_id', flat=True)
        for chan in cf_dist_channels:
            update_cf_config_with_trusted_signer(cf, chan, org.aws_account.account_id)

        live_dist = org.live_videos.all().values_list('cf_id', flat=True)

        for dist in live_dist:
            update_cf_config_with_trusted_signer(cf, dist, org.aws_account.account_id)

        org.security_enabled = True
        org.save()


def disable_signed_url_security(modeladmin, request, queryset):
    # After applying the change to the channels, change this to do it for each channel
    for org in queryset:
        cf = cloudfront.get_cloudfront_client(org.aws_account)

        # Update organization distribution trusted signers if exists
        if org.cf_id:
            update_cf_config_with_trusted_signer(cf, org.cf_id, org.aws_account.account_id)

        # Udpate channels distributions status
        cf_dist_channels = org.channels.all().values_list('cf_id', flat=True)
        for chan in cf_dist_channels:
            update_cf_config_without_trusted_signer(cf, chan)

        live_dist = org.live_videos.all().values_list('cf_id', flat=True)

        for dist in live_dist:
            update_cf_config_without_trusted_signer(cf, dist)

        org.security_enabled = False
        org.save()


def update_cf_config_with_trusted_signer(cf, cf_id, account_id):
    cf_conf = cf.get_distribution_config(Id=cf_id)
    cf_config_etag = cf_conf['ETag']
    cf_conf['DistributionConfig']['DefaultCacheBehavior']['TrustedSigners'] = {
        "Enabled": True,
        "Quantity": 1,
        "Items": [
            account_id
        ]
    }
    cf.update_distribution(
        Id=cf_id, IfMatch=cf_config_etag, DistributionConfig=cf_conf['DistributionConfig']
    )


def update_cf_config_without_trusted_signer(cf, cf_id):
    cf_conf = cf.get_distribution_config(Id=cf_id)
    cf_config_etag = cf_conf['ETag']
    cf_conf['DistributionConfig']['DefaultCacheBehavior']['TrustedSigners'] = {
        "Enabled": False,
        "Quantity": 0
    }
    cf.update_distribution(
        Id=cf_id, IfMatch=cf_config_etag, DistributionConfig=cf_conf['DistributionConfig']
    )


@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    actions = [disable_organization_data_traffic, enable_organization_data_traffic,
               enable_signed_url_security, disable_signed_url_security]
    list_display = (
    'id', 'name', 'contact_email', 'traffic_enabled', 'upload_enabled', 'security_enabled',)
    search_fields = ('name',)
    readonly_fields = ('traffic_enabled', 'security_enabled',)


@admin.register(Plan)
class PlanAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'video_transcoding', 'audio_transcoding', 'storage', 'data_transfer')
    search_fields = ('name',)


@admin.register(Bill)
class BillsAdmin(admin.ModelAdmin):
    list_display = ('id', 'organization', 'plan', 'date', 'last_modified')
    list_filter = ('organization',)
    search_fields = ('organization__name', 'plan__name',)


@admin.register(Channel)
class ChannelAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'organization', 'allowed_domains', 'detect_adblock')
    list_filter = ('organization',)
    search_fields = ('name', 'organization__name')


@admin.register(AWSAccount)
class AWSAccountAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'access_key', 'cf_key_pair_id')
    readonly_fields = ('display_secret_key',)

    def display_secret_key(self, obj):
        return '********'

    display_secret_key.short_description = 'Secret Access Key'

    def get_exclude(self, request, obj=None):
        excluded_fields = []
        if obj:
            excluded_fields.append('secret_access_key')

        return excluded_fields
