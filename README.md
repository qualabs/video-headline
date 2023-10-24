# Video Headline

![¡](docs/videoheadline_banner.jpg)

VideoHeadline is an open-source content management
system (CMS). It is a deployable solution that leverages the power of AWS services to manage and deliver both Video on Demand (VOD) and live video content. Built on the Django web framework, this CMS offers a user-friendly interface for content creators and administrators, making it easy to organize, publish and monitor video content.

![Browsing the App](docs/dashboard.gif)

## Table of Contents

- [Getting started](#getting-started)

  - [Prerequisites](#prerequisites)
  - [Create .env file](#create-.env-file)
  - [AWS Configuration](#aws-configuration)
  - [Running the application in local environment](#running-the-application-in-local-environment)
    - [Set up and running the application](#set-up-and-running-the-application)
    - [AWS Services Configuration in the Admin Web](#aws-services-configurationiin-the-admin-web)
- [Production Environment Tasks (optional)](#production-environment-tasks)
- [Custom CSS Configuration for the Player in an Organization](#Custom-css-configuration-for-the-player-in-an-organization)

## Getting started
### Prerequisites

- AWS Account: Necessary for hosting and delivering video content.
- Docker and Docker compose: Video Headline runs inside Docker containers, so it is necessary to have Docker and Docker Compose installed.
- Yarn and Node.js(v10): Required to deploy AWS configurations and build the playerReact component.
- Python: Necessary for running Django and other Python-based tools.
- AWS CLI: Useful for configuring and managing AWS services from the command line.

### Create .env file

Create a .env file at the root of the project with all the variables defined in the .env-example file and their respective values.

### AWS Configuration

Go to infrastructure directory and execute `yarn cdk deploy AwsConfigurationStack`.
   This will deploy:

- Api User with the following Permissions:
  - S3
  - Sns
  - MediaConvert
  - MediaLive
  - Cloudfront
  - Cloudwatch
- Media Convert Role with the following permissions:
  - Api Gateway
  - S3
- Media Live Role with the following permissions:
  - MediaLive
  - Cloudwatch

### Running the application in local environment
To set up the project locally, follow the instructions provided below. For AWS deployment, refer to the README within the Infrastructure folder.

**Environment Variables:** Add `AWS_MEDIA_CONVERT_ROLE` and `AWS_MEDIA_LIVE_ROLE` with respective ARNs to your Docker Compose file based on your environment (`docker-compose.dev.yml` or `docker-compose.prod.yml`).

#### Set up and running the application

Follow these steps to set up and run the application locally:

1. Create a symbolic link to the appropriate Docker Compose file (`docker-compose.dev.yml` or `docker-compose.prod.yml`) for your environment using `ln -s docker-compose.dev.yml docker-compose.yml`.
2. Run `docker-compose up`.
3. Run `docker exec -it video-hub bash` to access the video-hub container.
4. Create a superuser for admin access running `python manage.py createsuperuser`.
5. Go to `http://localhost:8010/admin` and log in with the superuser credentials.

#### AWS Services Configuration in the Admin Web

1. **CloudFront Configuration:** In the Global configuration, inside is the `CloudFront Configuration, apply the settings located in `configuration/configuration.samples/cloud_front_configuration.sample`.
2. **MediaConvert Configuration:** Create a `MediaConvert Configuration` named `default`, using the settings found in `configuration/configuration.samples/media_convert_configuration.sample`.
3. **MediaLive Configuration:** Create `MediaLive Configuration`, also named `default`, and apply the following configurations:
   - **Input Configuration:** `configuration/configuration.samples/media_live_input_attachments.sample`.
   - **Destination Configuration:** `configuration/configuration.samples/media_live_destinations.sample`.
   - **Encoder Configuration:** `configuration/configuration.samples/media_live_encoder_settings_economic.sample`.

![¡](docs/aws-services-configuration.png)

4. **Test Plan Creation:** Create a `Test Plan`, using the MediaLive and MediaConvert configurations.
5. **AWS Test Account:** Create a test `AWS Account`, and ensure it's equipped with the appropriate AWS credentials (These should be the credentials obtained in step 4(User permissions) of AWS Configuration).
6. **Test Organization:** Create a test `Organization`. This step will create an s3 bucket with the name of the organization, the name must follow the bucket naming rules: https://docs.aws.amazon.com/AmazonS3/latest/userguide/bucketnamingrules.html .

![¡](docs/orgs-and-channels.png)

7. **Superuser Association:** Assign the newly created Organization to the superuser to enable authentication via the User web (`http://localhost:3000/`). This can be done from the user detail section in the admin panel.

![¡](docs/auth.png)

### Production Environment Tasks (optional)

1. Schedule the following `Periodic Tasks` for MediaLive, CloudFront, and bill renewals:
   - `delete_channels` every hour.
   - `delete_inputs` every hour.
   - `check_live_cuts` every minute.
   - `delete_distributions` daily.
   - `bill_renewal` on the first day of every month.
2. If enabling statistics, set up qtracking for the organization.
3. If there are any modifications to the player, it’s essential to generate a new build.

### Custom CSS Configuration for the Player in an Organization

1. Have a URL ready with a CSS file to test (not a local path).
2. In the Organization, add the following line in the organization configuration field:

```
  "playerCustomCss":"https://your-css-url/cssFile.css"
```

If you do not have a CSS URL, you can serve a folder using the npx serve command: 1. Navigate to the folder containing the CSS file you want to use. 2. Run the command 'npx serve .'. 3. Open the server from the browser (probably http://localhost:5000), find the file, and copy the URL.