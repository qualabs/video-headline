import {
    App,
    Stack,
    aws_iam as iam,
    aws_secretsmanager as sm,
    SecretValue,
} from 'aws-cdk-lib'
export class AwsConfigurationStack extends Stack {
    readonly mediaConvertRole: iam.Role;
    readonly mediaLiveRole: iam.Role;
    readonly awsConfigSecret: sm.ISecret;

    constructor(scope: App, id: string) {
        super(scope, id);

        var accountId = Stack.of(this).account;
        //Inline policies
        const eventsRolePolicy = new iam.Policy(this, "EventsRole", {
            policyName: "EventsRole",
            document: iam.PolicyDocument.fromJson(
                {
                    "Version": "2012-10-17",
                    "Statement": [
                        {
                            "Sid": "Statement1",
                            "Effect": "Allow",
                            "Action": [
                                "events:*"
                            ],
                            "Resource": [
                                `arn:aws:events:us-east-1:${accountId}:rule/*`
                            ]
                        }
                    ]
                })
        })
        const mediaLivePassRolePolicy = new iam.Policy(this, "MediaLIvePassRole", {
            policyName: "MediaLIvePassRole",
            document: iam.PolicyDocument.fromJson(
                {
                    "Version": "2012-10-17",
                    "Statement": [
                        {
                            "Effect": "Allow",
                            "Action": [
                                "iam:PassRole"
                            ],
                            "Resource": "*"
                        }
                    ]
                })
        })

        //Api user
        const apiUser = new iam.User(this, "VideoheadlineApiUser", {
            userName: "VideoheadlineApiUser",
            managedPolicies: this.createManagedPolicies(),

        });
        apiUser.attachInlinePolicy(eventsRolePolicy);
        apiUser.attachInlinePolicy(mediaLivePassRolePolicy);

        const apiUserAccessKey = new iam.AccessKey(this, "ApiUserAccessKey", {
            user: apiUser,
        });


        this.awsConfigSecret = new sm.Secret(this, "ApiUserSecret", {
            secretName: "ApiUserSecret",
            secretObjectValue: {
                accessKeyId: SecretValue.unsafePlainText(apiUserAccessKey.accessKeyId),
                secretAccessKey: apiUserAccessKey.secretAccessKey,
            }
        });

        //Roles
        this.mediaConvertRole = new iam.Role(this, "MediaConvertRole", {
            roleName: "MediaConvertRole",
            assumedBy: new iam.ServicePrincipal("mediaconvert.amazonaws.com"),
            managedPolicies: [
                iam.ManagedPolicy.fromAwsManagedPolicyName("AmazonS3FullAccess"),
                iam.ManagedPolicy.fromAwsManagedPolicyName("AmazonAPIGatewayInvokeFullAccess"),
            ]
        })

        this.mediaLiveRole = new iam.Role(this, "MediaLiveAccessRole", {
            roleName: "MediaLiveAccessRole",
            assumedBy: new iam.ServicePrincipal("medialive.amazonaws.com"),
            managedPolicies: [
                iam.ManagedPolicy.fromAwsManagedPolicyName("AWSElementalMediaLiveFullAccess"),
                iam.ManagedPolicy.fromAwsManagedPolicyName("CloudWatchFullAccess"),
                iam.ManagedPolicy.fromAwsManagedPolicyName("AmazonS3FullAccess"),
            ]
        })
    }

    private createManagedPolicies() {

        const s3ManagedPolicy = iam.ManagedPolicy.fromAwsManagedPolicyName("AmazonS3FullAccess");
        const snsManagedPolicy = iam.ManagedPolicy.fromAwsManagedPolicyName("AmazonSNSFullAccess");
        const mediaConvertManagedPolicy = iam.ManagedPolicy.fromAwsManagedPolicyName("AWSElementalMediaConvertFullAccess");
        const mediaLiveManagedPolicy = iam.ManagedPolicy.fromAwsManagedPolicyName("AWSElementalMediaLiveFullAccess");
        const cloudFrontManagedPolicy = iam.ManagedPolicy.fromAwsManagedPolicyName("CloudFrontFullAccess");
        const cloudwatchManagedPolicy = iam.ManagedPolicy.fromAwsManagedPolicyName("CloudWatchLogsFullAccess");

        return [
            s3ManagedPolicy,
            snsManagedPolicy,
            mediaConvertManagedPolicy,
            mediaLiveManagedPolicy,
            cloudFrontManagedPolicy,
            cloudwatchManagedPolicy,
        ]
    }
}