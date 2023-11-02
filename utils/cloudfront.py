import boto3
from botocore.exceptions import ClientError
from celery import shared_task
from django.utils import timezone
from video.signals import cloudfront_deleted
from configuration.models import Configuration
from organization.models import AWSAccount


def get_cloudfront_client(aws_account):
    if aws_account:
        cloudfront = boto3.client(
            'cloudfront',
            aws_access_key_id=aws_account.access_key,
            aws_secret_access_key=aws_account.secret_access_key,
            region_name=aws_account.region,
        )
    else:
        cloudfront = boto3.client('cloudfront')
    return cloudfront


def create_distribution(settings, organization, channel):
    """
    Generate CloudFront distribution, use global default profile configuration.

    Replace conf settings, supplied values (keys):

        -id: origin id
        -domain: S3 bucker domain
        -target: origin Id
        -caller: operation unique id

    minimum set of target keys (from base node) in profile JSON config file:

            "Origins": { "Items": [{
                            "Id": origin id,
                            "DomainName": S3 bucker domain
                        }]
                    }

            "DefaultCacheBehavior": {
                "TargetOriginId": origin Id,
            }

            "CallerReference": operation unique id"

    See docs on [1]: https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/cloudfront.html#CloudFront.Client.create_distribution
                [2]: >> default profile configuration on /configuration/cloud_front_configuration.sample
    """

    global_config = Configuration.get_solo()
    conf_cont = global_config.cloud_front_configuration

    # get Origins/Items path, update & replace values
    origin_conf = conf_cont['Origins']['Items'][0]
    origin_conf['Id'] = settings['id']
    origin_conf['DomainName'] = settings['domain']
    conf_cont['Origins']['Items'] = [origin_conf]

    # get & update TargetOriginId path
    conf_cont['DefaultCacheBehavior']['TargetOriginId'] = settings['target']

    # get & update CallerReference path
    conf_cont['CallerReference'] = settings['caller']

    # assign a path if specified
    if settings.get('path'):
        origin_conf['OriginPath'] = settings['path']

    # change TTL of distribution if specified
    if settings.get('maxTTL') and settings.get('defaultTTL'):
        conf_cont['DefaultCacheBehavior']['DefaultTTL'] = settings['defaultTTL']
        conf_cont['DefaultCacheBehavior']['MaxTTL'] = settings['maxTTL']

    # Tags
    tags = {
        'Items': [
            {
                'Key': 'vh:org-id',
                'Value': str(organization.id),
            },
            {
                'Key': 'vh:channel-id',
                'Value': str(channel.id),
            },
        ]
    }

    DistributionConfigWithTags = {'DistributionConfig': conf_cont, 'Tags': tags}

    # create distribution
    cloudfront = get_cloudfront_client(organization.aws_account)
    new_dist = cloudfront.create_distribution_with_tags(
        DistributionConfigWithTags=DistributionConfigWithTags
    )

    # recover & return new CloudFront distribution Id & DomainName
    return {
        'cf_id': new_dist['Distribution']['Id'],
        'cf_domain': new_dist['Distribution']['DomainName'],
    }


def tag_distribution(organization, dist_id, tags):
    """
    tags = [(key, value), ... , (key, value)]
    """
    cloudfront = get_cloudfront_client(organization.aws_account)
    try:
        dist_arn = cloudfront.get_distribution(Id=dist_id)['Distribution']['ARN']

        cloudfront.tag_resource(
            Resource=dist_arn, Tags={'Items': [{'Key': k, 'Value': v} for k, v in tags]}
        )
    except ClientError as ex:
        # skip operation on distribution not exists operation
        if ex.response['Error']['Code'] == 'NoSuchDistribution':
            pass

        else:
            raise ex


def update_distribution(organization, dist_id, status=False):
    """
    If Organization is deleted the associated AWS CloudFront distribution
    should be previously deleted too.

    Steps:
        - retrieve distribution config
        - find & update 'Enabled' field value to disable distribution
        - send updated configuration

    See docs on [1]: https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/cloudfront.html#CloudFront.Client.get_distribution_config
                [2]: https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/cloudfront.html#CloudFront.Client.update_distribution
    """
    cloudfront = get_cloudfront_client(organization.aws_account)

    try:
        # GetDistributionConfig
        cf_config = cloudfront.get_distribution_config(Id=dist_id)
        cf_config_etag = cf_config['ETag']

        # update 'Enabled' field to False
        cf_config['DistributionConfig']['Enabled'] = status

        return cloudfront.update_distribution(
            Id=dist_id,
            IfMatch=cf_config_etag,
            DistributionConfig=cf_config['DistributionConfig'],
        )

    except ClientError as ex:
        # skip operation on distribution not exists operation
        if ex.response['Error']['Code'] == 'NoSuchDistribution':
            pass
        else:
            raise ex


def update_distribution_status(organization, dist_id, status=False):
    """
    If Organization is deleted the associated AWS CloudFront distribution
    should be previously deleted too.

    Steps:
        - retrieve distribution config
        - find & update 'Enabled' field value to disable distribution
        - send updated configuration

    See docs on [1]: https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/cloudfront.html#CloudFront.Client.get_distribution_config
                [2]: https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/cloudfront.html#CloudFront.Client.update_distribution
    """
    cloudfront = get_cloudfront_client(organization.aws_account)

    try:
        # GetDistributionConfig
        cf_config = cloudfront.get_distribution_config(Id=dist_id)
        cf_config_etag = cf_config['ETag']

        # update 'Enabled' field to False
        cf_config['DistributionConfig']['Enabled'] = status

        return cloudfront.update_distribution(
            Id=dist_id,
            IfMatch=cf_config_etag,
            DistributionConfig=cf_config['DistributionConfig'],
        )
    except ClientError as ex:
        # skip operation on distribution not exists operation
        if ex.response['Error']['Code'] == 'NoSuchDistribution':
            pass

        else:
            raise ex


def update_distribution_geoblocking(dist_id, type, location, organization):
    cloudfront = get_cloudfront_client(organization.aws_account)

    try:
        # GetDistributionConfig
        cf_config = cloudfront.get_distribution_config(Id=dist_id)
        cf_config_etag = cf_config['ETag']

        # Geoblocking
        cf_config = cf_config['DistributionConfig']
        cf_config['Restrictions']['GeoRestriction']['RestrictionType'] = type

        # Local import to avoid recursive import
        from video.models import LiveVideo

        if type == LiveVideo.GeoType.NONE:
            location = []

        cf_config['Restrictions']['GeoRestriction']['Quantity'] = len(location)
        cf_config['Restrictions']['GeoRestriction']['Items'] = location

        # upload new configuration
        return cloudfront.update_distribution(
            Id=dist_id, IfMatch=cf_config_etag, DistributionConfig=cf_config
        )

    except ClientError as ex:
        # skip operation on distribution not exists operation
        if ex.response['Error']['Code'] == 'NoSuchDistribution':
            pass
        else:
            raise ex


@shared_task
def delete_distributions():
    """
    Extract & mark for delete disabled CloudFront distributions.

    See docs on https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/cloudfront.html#CloudFront.Client.list_distributions
    """
    from organization.models import Channel
    from video.models import LiveVideo

    video_dist_used = list(Channel.objects.all().values_list('cf_id', flat=True))
    live_dist_used = list(LiveVideo.objects.all().values_list('cf_id', flat=True))
    dist_used = video_dist_used + live_dist_used
    for account in AWSAccount.objects.all():
        cloudfront = get_cloudfront_client(account)

        # get all distributions
        all_dist = cloudfront.list_distributions()
        all_dist = all_dist['DistributionList']['Items']

        # extract DEPLOYED and DISABLED distributions, important: only get Id
        disabled_distributions = list(
            filter(
                lambda dist_entry: dist_entry['Status'] == 'Deployed'
                and not dist_entry['Enabled'],
                all_dist,
            )
        )
        disabled_distributions = [dist['Id'] for dist in disabled_distributions]

        # enqueue for delete operation
        for dist_id in disabled_distributions:
            if dist_id not in dist_used:
                _delete_distribution.delay(dist_id, account.id)


@shared_task
def _delete_distribution(dist_id, aws_account_id):
    """
    Steps for delete distribution:
        - get distribution configuration
        - find a ETag operation value
        - perform a delete operation with Id and supplied ETag arguments

    See docs on [1]: https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/cloudfront.html#CloudFront.Client.get_distribution
                [2]: https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/cloudfront.html#CloudFront.Client.delete_distribution

    """
    cloudfront = get_cloudfront_client(
        AWSAccount.objects.get(account_id=aws_account_id)
    )

    try:
        # get distribution data (available keys: 'ResponseMetadata', 'ETag', 'Distribution')
        dist_conf = cloudfront.get_distribution(Id=dist_id)
        # get ETag operation value
        dist_etag = dist_conf['ETag']
        # perform a delete operation with Id and supplied ETag arguments

        cloudfront.delete_distribution(Id=dist_id, IfMatch=dist_etag)
    except Exception as e:
        _delete_distribution.retry(exc=e)


@shared_task
def _delete_cloudfront_distribution(
    dist_id, aws_account_id, video_id, retry_countdown=300
):
    """
    Steps for delete distribution:
        - get distribution configuration
        - find a ETag operation value
        - perform a delete operation with Id and supplied ETag arguments

    See docs on [1]: https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/cloudfront.html#CloudFront.Client.get_distribution
                [2]: https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/cloudfront.html#CloudFront.Client.delete_distribution

    """
    cloudfront = get_cloudfront_client(
        AWSAccount.objects.get(account_id=aws_account_id)
    )

    try:
        # get distribution data (available keys: 'ResponseMetadata', 'ETag', 'Distribution')
        dist_conf = cloudfront.get_distribution(Id=dist_id)
        # get ETag operation value
        dist_etag = dist_conf['ETag']
        # perform a delete operation with Id and supplied ETag arguments
        if dist_conf['Distribution']['Status'] == 'Deployed':
            cloudfront.delete_distribution(Id=dist_id, IfMatch=dist_etag)
            cloudfront_deleted.send(sender=None, video_id=video_id)
        else:
            _delete_cloudfront_distribution.retry(countdown=retry_countdown)
    except Exception as e:
        _delete_cloudfront_distribution.retry(countdown=retry_countdown)


def create_invalidation(organization, dist_id, paths):
    """
    Invalidates a cache of CloudFront
        - distribution_id: id of Cloudfront instance
        - paths: array of paths to invalidate
    """
    cloudfront = get_cloudfront_client(organization.aws_account)
    return cloudfront.create_invalidation(
        DistributionId=dist_id,
        InvalidationBatch={
            'Paths': {
                'Quantity': len(paths),
                'Items': paths,
            },
            'CallerReference': str(timezone.now().timestamp()).replace(".", ""),
        },
    )
