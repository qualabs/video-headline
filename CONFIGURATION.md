# Configuration

#### Creating a superuser

*Is assumed that by this time all images are running on docker. (check: - [Running the application in local environment](#running-the-application-in-local-environment))

1. Create a superuser for admin access running `python manage.py createsuperuser`.
2. Go to `http://localhost:8010/admin` and log in with the superuser credentials.

#### AWS Services Configuration in the Admin Web

*In order to apply this configurations, login to the admin web is needed.

1. **CloudFront Configuration:** Inside the Global configuration, apply the settings located in configuration/configuration.samples/cloud_front_configuration.sample on the CloudFront Configuration input.
2. **MediaConvert Configuration:** Create a `MediaConvert Configuration` named `default`, using the settings found in `configuration/configuration.samples/media_convert_configuration.sample`.
3. **MediaLive Configuration:** Create `MediaLive Configuration`, also named `default`, and apply the following configurations:
   - **Input Configuration:** `configuration/configuration.samples/media_live_input_attachments.sample`.
   - **Destination Configuration:** `configuration/configuration.samples/media_live_destinations.sample`.
   - **Encoder Configuration:** `configuration/configuration.samples/media_live_encoder_settings_economic.sample`.

   ![¡](docs/aws-services-configuration.png)
<!-- 
#### Using secure tokens with Cloudfront

*Cloudfront is used to deliver the Vod/live sources to the viewers, using the default configuration everything is set to Public, but we can change a few of this settings in order to have a more security and control.
 This properties are inside the configuration/configuration.samples/cloud_front_configuration.sample file

1. **ViewerProtocolPolicy:** Choose "Redirect HTTP to HTTPS" for enhanced security. -->

#### Creating a Plan

*On the "Organizations and channels" menu choose "Plans" and click on the "add plan" button.

![¡](docs/orgs-and-channels.png)

1. **Business name:** Add a name for the plan.
2. **Video transcoding configuration:** From the dropdown choose the configuration needed.
2. **Audio transcoding configuration:** From the dropdown choose the configuration needed.
3. **MediaLive Configuration:** From the dropdown choose the configuration needed.

![¡](docs/plan.png)

#### Adding a AWS account

*On the "Organizations and channels" menu choose "AWS account" and click on the "add AWS account" button.

1. **Name:** Add a name for the account.
2. **Access Key:** The Access Key for the API user (The user was created in the AWS Configuration section, and the credentials are available in AWS Secrets Manager).
3. **Secret Access Key:** The Secret Access Key for the API user (The user was created in the AWS Configuration section, and the credentials are available in AWS Secrets Manager).
4. **Region:** The region in which your AWS Account is deployed.
5. **MediaConvert Role:** On the AWS IAM service, on the "roles" section there is a search bar, which can be used to get the MediaConvertRole value.
6. **MediaConvert Endpoint URL** This value is on the "account" section of the Media Convert service in AWS.
7. **MediaLive Role:** On the AWS IAM service, on the "roles" section there is a search bar, which can be used to get the MediaLiveAccessRole value.
8. **Account Id:** Your AWS account number.

![¡](docs/aws-account.png)

#### Creating an Organization

*On the "Organizations and channels" menu choose "Organization" and click on the "add organization" button.

1. **Name:** Add a name for your organization. This step will create an s3 bucket with the name of the organization, the name must follow the bucket naming rules: https://docs.aws.amazon.com/AmazonS3/latest/userguide/bucketnamingrules.html .
2. **Plan:** From the dropdown choose the plan previously created.
3. **AWS Account:** From the dropdown choose the AWS Account previously created.

![¡](docs/organization.png)

#### Associatin an Organization to a user

*On the "Authentication and Authorization" menu choose "Users" and click on the username to edit.

1. **Organization:** Assign the newly created Organization to the superuser to enable authentication via the User web.

![¡](docs/auth.png)

### Custom CSS Configuration for the Player in an Organization

1. Have a URL ready with a CSS file to test (not a local path).
2. In the Organization, add the following line in the organization configuration field:

```
  "playerCustomCss":"https://your-css-url/cssFile.css"
```

If you do not have a CSS URL, you can serve a folder using the npx serve command: 1. Navigate to the folder containing the CSS file you want to use. 2. Run the command 'npx serve .'. 3. Open the server from the browser (probably http://localhost:5000), find the file, and copy the URL.