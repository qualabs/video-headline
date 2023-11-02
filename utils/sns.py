import boto3
import json


class NotificationNotFoundException(Exception):
    def __init__(self, message=''):
        self.message = message


def get_sns(aws_account):
    if aws_account:
        sns = boto3.client(
            'sns',
            aws_access_key_id=aws_account.access_key,
            aws_secret_access_key=aws_account.secret_access_key,
            region_name=aws_account.region,
        )
    else:
        sns = boto3.client('sns')

    return sns


def create_topic(live):
    sns = get_sns(live.organization.aws_account)

    response = sns.create_topic(Name=str(live.video_id))
    topic_arn = response['TopicArn']

    attributes = sns.get_topic_attributes(TopicArn=topic_arn)
    policy = json.loads(attributes['Attributes']['Policy'])

    new_policy = {
        'Sid': 'Allow_Publish_Events',
        'Effect': 'Allow',
        'Principal': {'Service': 'events.amazonaws.com'},
        'Action': 'sns:Publish',
        'Resource': topic_arn,
    }

    policy['Statement'].append(new_policy)

    # Allow eventbridge to publish messages
    sns.set_topic_attributes(
        TopicArn=topic_arn, AttributeName='Policy', AttributeValue=json.dumps(policy)
    )

    return topic_arn


def delete_topic(live):
    sns = get_sns(live.organization.aws_account)
    sns.delete_topic(TopicArn=live.sns_topic_arn)


def subscribe(live, endpoint):
    sns = get_sns(live.organization.aws_account)

    response = sns.subscribe(
        TopicArn=live.sns_topic_arn,
        Protocol='https',
        Endpoint=endpoint,
        ReturnSubscriptionArn=True,
    )

    # return subscription arn if ReturnSubscriptionArn is true, else return "pending confirmation"
    return response


def list_subscriptions_by_topic(live):
    sns = get_sns(live.organization.aws_account)

    response = sns.list_subscriptions_by_topic(TopicArn=live.sns_topic_arn)

    return response['Subscriptions']


def unsubscribe(live, arn):
    sns = get_sns(live.organization.aws_account)
    sns.unsubscribe(SubscriptionArn=arn)


def unsubscribe_all(live):
    sns = get_sns(live.organization.aws_account)
    subscription_arns = sns.list_subscriptions_by_topic(TopicArn=live.sns_topic_arn)

    for subscription in subscription_arns['Subscriptions']:
        try:
            sns.unsubscribe(SubscriptionArn=subscription['SubscriptionArn'])
        except (
            sns.exceptions.InvalidParameterException,
            sns.exceptions.NotFoundException,
        ):
            continue
