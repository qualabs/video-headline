import botocore

ADD_ORG_ERROR = "Something went wrong creating the organization, please check the logs for more information."
INVALID_ORG_NAME = "Organization name is not valid. Please try a different name"
DELETE_ORG_ERROR = "Error deleting Organization"
DELETE_VIDEO_ERROR = "Error deleting video"

#Message colors
FAIL = '\033[91m'

def is_no_such_bucket_error(ex):
    return (
        isinstance(ex, botocore.exceptions.ClientError) and
        'NoSuchBucket' in ex.response['Error']['Code']
        )

def is_bucket_already_exist_error(ex):
    return (
        isinstance(ex, botocore.exceptions.ClientError) and
        'BucketAlreadyExists' in ex.response['Error']['Code']
        )

def print_error(error):
    print(FAIL + str(error))

