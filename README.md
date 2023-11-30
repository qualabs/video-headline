# Video Headline

![¡](docs/videoheadline_banner.jpg)

VideoHeadline is an open-source content management
system (CMS). It is a deployable solution that leverages the power of AWS services to manage and deliver both Video on Demand (VOD) and live video content. Built on the Django web framework, this CMS offers a user-friendly interface for content creators and administrators, making it easy to organize, publish and monitor video content.

![Browsing the App](docs/dashboard.gif)

## Deploy VideoHeadline

Deploy a stable version of VideoHeadline using a pre-built docker-hub image for a quick and easy deployment process.
Alternatively, you can build the image locally to deploy a customized version of VideoHeadline, changing the code and its configuration files (see [Table of extra contents](#table-of-extra-contents) for more information).

### Prerequisites

- AWS account (it's not necessary to have any profile configured locally).
- Docker running on your machine.

### Steps to deploy VideoHeadline Infrastructure

1. Run deployment: `docker run -e AWS_ACCESS_KEY_ID=... -e AWS_SECRET_ACCESS_KEY=... -e AWS_SESSION_TOKEN=... -e PROCESS=deploy -it qualabs/video-headline-deploy`

   - AWS_ACCESS_KEY_ID: AWS access key identifier.
   - AWS_SECRET_ACCESS_KEY: AWS secret access key.
   - AWS_SESSION_TOKEN: AWS session token (if required).

   These variables can be found in AWS Command line or programmatic access.

2. Once the implementation process has started through the console, you may be asked to confirm with a y/n, please confirm it.

3. The url of the application will be displayed in the console.

4. At the end of this deploy process, a superuser will be created to use in the application, you will be asked via console for the data you want to use.

### Accessing the App

Once the app is deployed you can access the web through the previously mentioned url. If you want to access the Admin web you need to add /admin to the app base URL.

## Table of extra contents

- Deploy VideoHeadline to AWS
  - See [README.md](infrastructure/README.md) within the Infrastructure folder.
- Want to develop locally and contribute?
  - See [CONTRIBUTING.md](CONTRIBUTING.md).
- Want to personalize the AWS Services configurations, users and other settings?
  - See [Configuration.md](CONFIGURATION.md).
