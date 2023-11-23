# Video Headline CDK Deployment
The `cdk.json` file tells the CDK Toolkit how to execute your app.

## Getting started
### Prerequisites
- AWS CLI installed and configured with at least one profile.
- Docker running on your machine.
### Steps to deploy Videoheadline Infrastructure
1. Install the required dependencies: `yarn install`.

2. Build the project: `yarn run build` .

3. Bootstrap the CDK app: `yarn cdk bootstrap`. If you are using a specific AWS profile, include the `--profile` flag: `yarn cdk bootstrap --profile [...]` (replace `[...]` with your AWS profile). If no profile flag is specified, the default profile will be used.

4. Deploy the app: `yarn cdk deploy '*' --profile [...]`

## Getting started
### Accessing the App
Once the app is deployed you can access the web through Videoheadline Cloudfront using the Distribution domain name.
If you want to access the Admin web you need to add /admin to the Distribution domain name.
# Creating superuser
## Prerequisites
- You need to install AWS Session manager plugin (https://docs.aws.amazon.com/systems-manager/latest/userguide/session-manager-working-with-install-plugin.html).
- You need to configure your AWS_PROFILE env variable.

## Running the create_super_user.py script
To create a superuser run `python create_super_user.py`

A superuser with the data configured in create_super_user.sh will be created.

You can edit the file to create the superuser as desired. Take into account you need to edit it before delploying, since the script
that gets executed is the one that is copied to the container.
## Useful commands
-   `yarn run build` compile typescript to js
-   `yarn run watch` watch for changes and compile
-   `yarn run test` perform the jest unit tests
-   `yarn cdk deploy` deploy this stack to your default AWS account/region
-   `yarn cdk diff` compare deployed stack with current state
-   `yarn cdk synth` emits the synthesized CloudFormation template
## Configuring HTTPS
If you want to configure https with a certificate you can put your certificate arn in `/lib/utils/aws.ts`. (https://github.com/qualabs/video-headline/blob/cca91831ef0130ea1fefa53084b949308d55c57e/infrastructure/lib/utils/aws.ts#L25).

# Remove

If you want to remove all the resources deployed you can run `yarn cdk destroy '*' --profile [...]`
