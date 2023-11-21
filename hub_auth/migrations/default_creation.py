import boto3
def create_periodic_tasks(apps, schema_editor):
    PeriodicTask = apps.get_model('djcelery', 'PeriodicTask')
    PeriodicTask.objects.create(
        name='Delete Channels',
        task='hub.tasks.delete_channels',
        interval=3600,
        enabled=True,
    )
    PeriodicTask.objects.create(
        name='Delete Inputs',
        task='hub.tasks.delete_inputs',
        interval=3600,
        enabled=True,
    )
    PeriodicTask.objects.create(
        name='Check Live Cuts',
        task='hub.tasks.check_live_cuts',
        interval=60,
        enabled=True,
    )
    PeriodicTask.objects.create(
        name='Delete Distributions',
        task='hub.tasks.delete_distributions',
        interval=86400,
        enabled=True,
    )
    PeriodicTask.objects.create(
        name='Bill Renewal',
        task='hub.tasks.bill_renewal',
        interval=2592000,
        enabled=True,
    )


def get_iam_role_arn(role_name):
    iam_client = boto3.client('iam')

    try:
        response = iam_client.get_role(RoleName=role_name)
        role_arn = response['Role']['Arn']
    except iam_client.exceptions.NoSuchEntityException:
        print(f"IAM role '{role_name}' not found.")

    return role_arn

def get_secret(secret_name):
    secret_client = boto3.client('secretsmanager')

    try:
        response = secret_client.get_secret_value(SecretId=secret_name)
        secret_data = response['SecretString']
        secret_json = json.loads(secret_data)
        access_key = secret_json.get('accessKeyId')
        secret_access_key = secret_json.get('secretAccessKey')
    except secret_client.exceptions.ResourceNotFoundException:
        print(f"Secret with name '{secret_name}' not found in Secrets Manager.")
        access_key, secret_access_key = None, None

    return access_key, secret_access_key

def get_media_convert_endpoint_url():
    mediaconvert_client = boto3.client('mediaconvert')

    try:
        response = mediaconvert_client.describe_endpoints()
        endpoint_url = response['Endpoints'][0]['Url']
    except (IndexError, KeyError):
        print("Unable to retrieve MediaConvert endpoint URL.")
        endpoint_url = None

    return endpoint_url
    #Default configuration
def create_default_objects(apps, schema_editor):
    AWSAccount = apps.get_model('organization', 'AWSAccount')
    secret_name = 'ApiUserSecret'

    access_key, secret_access_key = get_secret(secret_name)

    media_convert_role_name = 'MediaConvertRole'
    media_live_role_name = 'MediaLiveAccessRole'

    media_convert_role_arn = get_iam_role_arn(media_convert_role_name)
    media_live_role_arn = get_iam_role_arn(media_live_role_name)

    media_convert_endpoint_url = get_media_convert_endpoint_url()

    aws_account_defaults = {
        'name': 'Default AWS Account',
        'access_key': access_key,
        'secret_access_key': secret_access_key,
        'media_live_role': media_live_role_arn,
        'media_convert_role': media_convert_role_arn,
        'region': os.environ.get('AWS_DEFAULT_REGION'),
        'media_convert_endpoint_url': media_convert_endpoint_url,
        'account_id': os.environ.get('AWS_ACCOUNT_ID'),
        

        # TODO: Add other fields with default values as needed
    }

    AWSAccount.objects.create(**aws_account_defaults)
