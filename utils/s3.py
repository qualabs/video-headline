import boto3
import hashlib
import hmac
import json
import re
import os
from botocore.exceptions import BotoCoreError
from utils.cloudfront import get_cloudfront_client


def get_s3_client(aws_account):
    if aws_account:
        s3 = boto3.client(
            "s3",
            aws_access_key_id=aws_account.access_key,
            aws_secret_access_key=aws_account.secret_access_key,
            region_name=aws_account.region,
        )
    else:
        s3 = boto3.client("s3")
    return s3


def get_s3_resource(aws_account):
    if aws_account:
        s3 = boto3.resource(
            "s3",
            aws_access_key_id=aws_account.access_key,
            aws_secret_access_key=aws_account.secret_access_key,
            region_name=aws_account.region,
        )
    else:
        s3 = boto3.resource("s3")
    return s3


def get_put_presigned_s3_url(
    organization, path_to_file, content_type, acl_policy="private"
):
    """
    Generate a Signed URL to put an object in a S3's bucket
    """

    aws_account = organization.aws_account
    s3 = get_s3_client(aws_account)

    url = s3.generate_presigned_url(
        ClientMethod="put_object",
        Params={
            "Bucket": organization.bucket_name,
            "Key": path_to_file,
            "ContentType": content_type,
            "ACL": acl_policy,
        },
    )

    return url


def generate_bucket_name(bucket_name):
    """
    Create trusted AWS s3 bucket name for a new organization.
    The name is generated from Organization name.
    Multiples validations are performed (see details below).

        Validation:
            - extract allowed characters only: alphanumerical and dashes.
            - verify max (63) and min (3) characters length.
    """
    bucket_name = "-".join(re.findall("[a-z0-9-]+", bucket_name.lower()))

    if len(bucket_name) > 63:
        bucket_name = bucket_name[:63]

    if len(bucket_name) < 3:
        bucket_name = bucket_name.ljust(3, "-")

    # return trusted bucket name
    return bucket_name


def create_bucket(organization):
    """
    Create a new AWS s3 bucket after that a new organization is saved.

    See docs on [1]: https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html#S3.Client.create_bucket
                [2]: https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html#S3.Client.put_bucket_cors

    """
    s3 = get_s3_client(organization.aws_account)
    new_bucket = s3.create_bucket(Bucket=organization.bucket_name)

    # put CORS configuration
    cors_configuration = {
        "CORSRules": [
            {
                "AllowedMethods": ["GET", "PUT", "POST", "DELETE"],
                "AllowedOrigins": ["*"],
                "AllowedHeaders": ["*"],
                "ExposeHeaders": [
                    "ETag",
                    "x-amz-server-side-encryption",
                    "x-amz-request-id",
                    "x-amz-id-2",
                ],
            }
        ]
    }
    s3.put_bucket_cors(
        Bucket=organization.bucket_name, CORSConfiguration=cors_configuration
    )

    statement_list = [
        {
            "Sid": "Stmt1551893580619",
            "Effect": "Allow",
            "Principal": "*",
            "Action": ["s3:PutObject", "s3:GetObject"],
            "Resource": [
                f"arn:aws:s3:::{organization.bucket_name}/*/hls/*",
                f"arn:aws:s3:::{organization.bucket_name}/live/*",
                f"arn:aws:s3:::{organization.bucket_name}/*/thumbs/*",
                f"arn:aws:s3:::{organization.bucket_name}/*/audio/*",
            ],
        },
        {
            "Sid": "Stmt1579890871869",
            "Effect": "Allow",
            "Principal": "*",
            "Action": "s3:ListBucket",
            "Resource": f"arn:aws:s3:::{organization.bucket_name}",
        },
    ]

    cloudfront_id = os.getenv("CLOUDFRONT_ID", None)
    if cloudfront_id:
        cloudfront_client = get_cloudfront_client(organization.aws_account)
        response = cloudfront_client.get_distribution(Id=cloudfront_id)

        cloudfront_arn = response["Distribution"]["ARN"]
        statement_list.append(
            {
                "Sid": "AllowCloudFrontServicePrincipalReadOnly",
                "Effect": "Allow",
                "Principal": {"Service": "cloudfront.amazonaws.com"},
                "Action": "s3:GetObject",
                "Resource": [
                    f"arn:aws:s3:::{organization.bucket_name}/*/hls/*",
                    f"arn:aws:s3:::{organization.bucket_name}/*/dash/*",
                    f"arn:aws:s3:::{organization.bucket_name}/live/*",
                    f"arn:aws:s3:::{organization.bucket_name}/*/thumbs/*",
                    f"arn:aws:s3:::{organization.bucket_name}/*/audio/*",
                ],
                "Condition": {"StringEquals": {"AWS:SourceArn": f"{cloudfront_arn}"}},
            }
        )

    # put POLICY configuration
    bucket_policy = {
        "Version": "2012-10-17",
        "Statement": statement_list,
    }

    block_public_policy = {
        "BlockPublicAcls": False,
        "IgnorePublicAcls": False,
        "BlockPublicPolicy": False,
        "RestrictPublicBuckets": False,
    }

    s3.put_public_access_block(
        Bucket=organization.bucket_name,
        PublicAccessBlockConfiguration=block_public_policy,
    )
    s3.put_bucket_policy(
        Bucket=organization.bucket_name, Policy=json.dumps(bucket_policy)
    )

    return new_bucket


def get_size(organization, bucket_name, prefix):
    s3 = get_s3_resource(organization.aws_account)
    total_size = 0
    for obj in s3.Bucket(bucket_name).objects.filter(Prefix=prefix):
        total_size += obj.size
    return total_size


def delete_bucket(organization):
    """
    If Organization is deleted the associated AWS s3 bucket should be previously deleted too.

    See docs on https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html#S3.Client.delete_bucket
    """

    s3 = get_s3_client(organization.aws_account)

    try:
        # perform delete operation & catch errors
        return s3.delete_bucket(Bucket=organization.bucket_name)
    except (ClientError, BotoCoreError):
        # skip operation on bucket not exists operation
        pass


def delete_object(bucket_name, key, aws_account):
    s3 = get_s3_resource(aws_account)
    bucket = s3.Bucket(bucket_name)
    try:
        return bucket.objects.filter(Prefix=key).delete()
    except BotoCoreError:
        pass


def sign(key, msg):
    return hmac.new(key, msg.encode("utf-8"), hashlib.sha256).digest()


def get_signature_key(key, date_stamp, region_name, service_name):
    k_date = sign(("AWS4" + key).encode("utf-8"), date_stamp)
    k_region = sign(k_date, region_name)
    k_service = sign(k_region, service_name)
    k_signing = sign(k_service, "aws4_request")

    return k_signing
