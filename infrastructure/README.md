# VideoHeadline CDK Deployment
# Table of Contents
- [Deployment](#Deployment)
    - [Use pre-build image](#Use-pre-build-image)
    - [Use local image](#use-local-image)
- [Destroy](#Destroy)
    - [Destroy deployment using pre-built image](#destroy-deployment-using-pre-built-image)
    - [Destroy deployment using local image](#destroy-deployment-using-local-image)
- [Useful commands](#useful-commands)
- [Configuring HTTPS](#configuring-https)

# Deployment
To deploy VideoHeadline in AWS there are two alternatives. The first involves using a stable VideoHeadline version (main), so there is already a built image that exists in docker-hub and the deploy process will use this image. 
The second alternative involves building VideoHeadline image before performing  deploy process, this can be used to make changes locally and to perform a deploy without depending on the version of main
## Use pre-build image
### Prerequisites
- AWS account (it's not necessary to have any profile configured locally).
- Docker running on your machine.
### Steps to deploy VideoHeadline Infrastructure
1. Build deployment image: `docker build -t video-headline-deploy .`

2. Run deployment: `docker run -e AWS_ACCESS_KEY_ID=... -e AWS_SECRET_ACCESS_KEY=... -e AWS_SESSION_TOKEN=... -e PROCESS=deploy -it video-headline-deploy`
    - AWS_ACCESS_KEY_ID: AWS access key identifier.
    - AWS_SECRET_ACCESS_KEY: AWS secret access key.
    - AWS_SESSION_TOKEN: AWS session token (if required).

   These variables can be found in AWS Command line or programmatic access.


3. Once the implementation process has started through the console, you may be asked to confirm with a y/n, please confirm it.

3. The url of the application will be displayed in the console

4. At the end of this deploy process, a superuser will be created to use in the application, you will be asked via console for the data you want to use.

### Accessing the App
Once the app is deployed you can access the web through the previously mentioned url. If you want to access the Admin web you need to add /admin to the Distribution domain name.

## Use local image
### Prerequisites
- AWS CLI installed and configured with at least one profile.
- Docker running on your machine.
### Steps to deploy Videoheadline Infrastructure
1. Install the required dependencies: `yarn install`.

2. Build the project: `yarn run build` .

3. Bootstrap the CDK app: `yarn cdk bootstrap`.
    - If you are using a specific AWS profile, include the `--profile` flag: `yarn cdk bootstrap --profile [...]` (replace `[...]` with your AWS profile). If no profile flag is specified, the default profile will be used.

4. Deploy the app: `yarn cdk deploy '*'`
    - If you are using a specific AWS profile, include the `--profile` flag: `yarn cdk deploy '*' --profile [...]` (replace `[...]` with your AWS profile). If no profile flag is specified, the default profile will be used.

5. Once the implementation process has started through the console, you may be asked to confirm with a y/n, please confirm it.

6. The url of the application will be displayed in the console

### Creating superuser
#### Prerequisites
- You need to install AWS Session manager plugin (https://docs.aws.amazon.com/systems-manager/latest/userguide/session-manager-working-with-install-plugin.html).
- You need to configure your AWS_PROFILE env variable.

#### Running the create_super_user.py script
To create a superuser run `python create_super_user.py`

A superuser with the data configured in create_super_user.sh will be created.

You can edit the file to create the superuser as desired. Take into account you need to edit it before delploying, since the script
that gets executed is the one that is copied to the container.
### Accessing the App
Once the app is deployed you can access the web through the previously mentioned url. If you want to access the Admin web you need to add /admin to the Distribution domain name.

# Destroy

## Destroy deployment using pre-built image
- If you want to remove all the resources deployed you can run: `docker run -e AWS_ACCESS_KEY_ID=... -e AWS_SECRET_ACCESS_KEY=... -e AWS_SESSION_TOKEN=... -e PROCESS=destroy -it video-headline-deploy`
    - AWS_ACCESS_KEY_ID: AWS access key identifier.
    - AWS_SECRET_ACCESS_KEY: AWS secret access key.
    - AWS_SESSION_TOKEN: AWS session token (if required).

   These variables can be found in AWS Command line or programmatic access.


## Destroy deployment using local image

- If you want to remove all the resources deployed you can run: `yarn cdk destroy '*' --profile [...]`

# Useful commands
-   `yarn run build` compile typescript to js
-   `yarn run watch` watch for changes and compile
-   `yarn run test` perform the jest unit tests
-   `yarn cdk deploy` deploy this stack to your default AWS account/region
-   `yarn cdk diff` compare deployed stack with current state
-   `yarn cdk synth` emits the synthesized CloudFormation template
# Configuring HTTPS
If you want to configure https with a certificate you can put your certificate arn in `/lib/utils/aws.ts`. (https://github.com/qualabs/video-headline/blob/cca91831ef0130ea1fefa53084b949308d55c57e/infrastructure/lib/utils/aws.ts#L25).