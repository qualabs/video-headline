# Configuration

#### AWS Services Configuration in the Admin Web

1. **CloudFront Configuration:** Inside the Global configuration, apply the settings located in `configuration/configuration.samples/cloud_front_configuration.sample`on the CloudFront Configuration input.
2. **MediaConvert Configuration:** Create a `MediaConvert Configuration` named `default`, using the settings found in `configuration/configuration.samples/media_convert_configuration.sample`.
3. **MediaLive Configuration:** Create `MediaLive Configuration`, also named `default`, and apply the following configurations:
   - **Input Configuration:** `configuration/configuration.samples/media_live_input_attachments.sample`.
   - **Destination Configuration:** `configuration/configuration.samples/media_live_destinations.sample`.
   - **Encoder Configuration:** `configuration/configuration.samples/media_live_encoder_settings_economic.sample`.

   ![¡](docs/aws-services-configuration.png)

4. **Plan Creation:** Create a test `Plan`, using the MediaLive and MediaConvert configurations.
5. **AWS Account:** Create a test `AWS Account`, and ensure it's equipped with the appropriate AWS credentials (These should be the API user's credentials created in AWS Configuration section which are available in AWS Secrets Manager).
6. **Organization:** Create a test `Organization`. This step will create an s3 bucket with the name of the organization, the name must follow the bucket naming rules: https://docs.aws.amazon.com/AmazonS3/latest/userguide/bucketnamingrules.html .

![¡](docs/orgs-and-channels.png)

7. **Superuser Association:** Assign the newly created Organization to the superuser to enable authentication via the User web (`http://localhost:3000/`). This can be done from the user detail section in the admin panel.

![¡](docs/auth.png)