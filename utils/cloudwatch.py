import boto3
from datetime import datetime, timedelta


def get_cloudwatch(aws_account):
    if aws_account:
        cloudwatch = boto3.client('cloudwatch', aws_access_key_id=aws_account.access_key,
                                  aws_secret_access_key=aws_account.secret_access_key,
                                  region_name=aws_account.region)
    else:
        cloudwatch = boto3.client('cloudwatch')

    return cloudwatch


def get_storage(aws_account, bucket_name):
    cloudwatch = get_cloudwatch(aws_account)
    response = cloudwatch.get_metric_statistics(
        Namespace="AWS/S3",
        MetricName="BucketSizeBytes",
        Dimensions=[
            {
                "Name": "BucketName",
                "Value": bucket_name
            },
            {
                "Name": "StorageType",
                "Value": "StandardStorage"
            }
        ],
        StartTime=datetime.now() - timedelta(days=2),
        EndTime=datetime.now(),
        Period=86400,
        Statistics=['Average']
    )

    if len(response['Datapoints']) > 0:
        # Result of storage in bytes then converted to GB
        return response['Datapoints'][-1]['Average'] / (1024 ** 3)
    return 0
