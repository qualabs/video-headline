#!/usr/bin/env node
import 'source-map-support/register';
import { App, Tags } from 'aws-cdk-lib';
import { VideoheadlineStack } from '../lib/videoheadline-stack';
import { defaultTags } from '../lib/utils/aws';
import { AwsConfigurationStack } from '../lib/aws-configuration-stack';

const app = new App();

const tags: Object = defaultTags();

Object.entries(tags).forEach(([key, value]) => {
    Tags.of(app).add(key, value);
});

const awsConfigStack = new AwsConfigurationStack(app, 'AwsConfigurationStack');
new VideoheadlineStack(app, 'VideoheadlineStack', {
    mediaConvertRole: awsConfigStack.mediaConvertRole,
    mediaLiveRole: awsConfigStack.mediaLiveRole,
    awsConfigSecret: awsConfigStack.awsConfigSecret,
});
