
# User Permisisons
  
## User should have the following permissions

1. AmazonS3FullAccess
2. AmazonSNSFullAccess
3. AWSElementalMediaConvertFullAccess
4. AWSElementalMediaLiveFullAccess
5. CloudFrontFullAccess
6. Custom Policy for EventBridge:

```
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
                "arn:aws:events:us-east-1:111122223333:rule/*"
            ]
        }
    ]
}
```

7. Custom Policy for MediaLive Pass Role:

```
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
}
```