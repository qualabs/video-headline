import {
    App,
    Stack,
    StackProps,
    Duration,
    aws_ecs as ecs,
    aws_ecr as ecr,
    aws_ec2 as ec2,
    aws_elasticloadbalancingv2 as elb,
    aws_certificatemanager,
    aws_rds as db,
    aws_secretsmanager as sm,
    RemovalPolicy,
    aws_cloudfront,
    aws_cloudfront_origins,
    CfnOutput,
} from 'aws-cdk-lib';
import { DockerImageAsset } from 'aws-cdk-lib/aws-ecr-assets';
import { join } from 'path';
import * as ecrdeploy from 'cdk-ecr-deployment';
import { taskDefinitionEnvironment, videoHubtaskDefinitionEnvironment, qhubDevCertArn } from './utils/aws';
import { RedisCluster } from './redis-cluster';
import * as iam from 'aws-cdk-lib/aws-iam';

const engineVersion = db.PostgresEngineVersion.of('11.21', '11');
const storageTypes = db.StorageType.GP2;

export interface VideoheadlineStackProps extends StackProps {
    mediaConvertRole: iam.Role;
    mediaLiveRole: iam.Role;
    awsConfigSecret: sm.ISecret;
}

const isProduction = process.env.VIDEOHEADLINE_IMAGE === 'production';

export class VideoheadlineStack extends Stack {
    vpc: ec2.IVpc;
    readonly database: db.IDatabaseInstance;
    readonly dbSecret: sm.ISecret;

    constructor(scope: App, id: string, props: VideoheadlineStackProps) {
        super(scope, id);

        // VPC (Virtual Private Cloud)   
        this.createVPC();

        // SecurityGroup
        const securityGroup = new ec2.SecurityGroup(this, 'security-group-vh', {
            vpc: this.vpc,
            description: 'videoheadline security group',
            allowAllOutbound: true,
            securityGroupName: 'videoheadline-security-group'
        });

        // Database instance
        const vhDatabase = this.createDB(securityGroup);
        this.database = vhDatabase;
        this.dbSecret = vhDatabase.secret!;

        // ECS (Elastic Container Service) cluster with a Redis cluster and KMS encryption key
        const qhubRedisCluster = new RedisCluster(this, 'vh-redis-cluster', {
            vpc: this.vpc,
            sg: securityGroup,
        });

        const vhCluster = new ecs.Cluster(this, 'VideoheadlineCluster', {
            clusterName: 'Videoheadline-cluster',
            vpc: this.vpc,
        });

        //Task definitions
        const vhCeleryTaskDefinition = new ecs.FargateTaskDefinition(
            this,
            'celeryTask',
            {
                memoryLimitMiB: 1024,
                cpu: 512,
            }
        );
        const videoHubTaskDefinition = new ecs.FargateTaskDefinition(
            this,
            'videoHubTask',
            {
                memoryLimitMiB: 1024,
                cpu: 512,
            }
        );

        // Adding role to enable connection to containers
        const ecsTaskRole = new iam.Role(this, "EcsTaskRole", {
            roleName: "EcsTaskRole",
            assumedBy: new iam.ServicePrincipal("ecs-tasks.amazonaws.com"),

        })
        ecsTaskRole.addToPolicy(
            new iam.PolicyStatement({
                effect: iam.Effect.ALLOW,
                actions: ['ssmmessages:CreateControlChannel', 'ssmmessages:CreateDataChannel', 'ssmmessages:OpenControlChannel', 'ssmmessages:OpenDataChannel'],
                resources: ['*']
            })
        );
        ecsTaskRole.grantAssumeRole(new iam.ServicePrincipal("ecs-tasks.amazonaws.com"))

        // Adding policies to enable connection to containers
        videoHubTaskDefinition.addToTaskRolePolicy(
            new iam.PolicyStatement({
                effect: iam.Effect.ALLOW,
                actions: ['ssmmessages:CreateControlChannel', 'ssmmessages:CreateDataChannel', 'ssmmessages:OpenControlChannel', 'ssmmessages:OpenDataChannel'],
                resources: ['*']
            }),
        );

        // ECR (Elastic Container Registry) repository
        const vhEcr = new ecr.Repository(this, 'vhRepository', {
            repositoryName: 'vh-repository',
            removalPolicy: RemovalPolicy.DESTROY,
            autoDeleteImages: true
        });

        const vhLoadBalancer = new elb.ApplicationLoadBalancer(
            this,
            'videoHeadlineLB',
            {
                vpc: this.vpc,
                vpcSubnets: this.vpc.selectSubnets({
                    subnetType: ec2.SubnetType.PUBLIC,
                    onePerAz: true,
                }),
                internetFacing: true,
                loadBalancerName: 'VideoHeadline-LB',
                ipAddressType: elb.IpAddressType.IPV4,
                http2Enabled: true,
            }
        );
        const loadbalancerUrl = vhLoadBalancer.loadBalancerDnsName;
        const videoheadlineCF = new aws_cloudfront.Distribution(this, 'VideoheadlineCF', {
            defaultBehavior: {
                origin: new aws_cloudfront_origins.HttpOrigin(loadbalancerUrl, {
                    protocolPolicy: aws_cloudfront.OriginProtocolPolicy.HTTP_ONLY,
                }),
                allowedMethods: aws_cloudfront.AllowedMethods.ALLOW_ALL,
                cachePolicy: aws_cloudfront.CachePolicy.CACHING_DISABLED,
                originRequestPolicy: aws_cloudfront.OriginRequestPolicy.ALL_VIEWER,
                viewerProtocolPolicy: aws_cloudfront.ViewerProtocolPolicy.REDIRECT_TO_HTTPS
            },
            comment: 'Videoheadline',
        });
        
        console.log("Cloudfront URL: ", videoheadlineCF.domainName)
        new CfnOutput(this, "CfnOutCloudfrontUrl", { value: videoheadlineCF.domainName, description: "CloudFront URL", });

        // Containers
        videoHubTaskDefinition.addContainer('videoheadline', {
            image: new ecs.EcrImage(vhEcr, 'latest'),
            environment: videoHubtaskDefinitionEnvironment(
                this.database.instanceEndpoint.hostname,
                qhubRedisCluster.redisEndpoint,
                props.mediaConvertRole.roleArn,
                props.mediaLiveRole.roleArn,
                videoheadlineCF.domainName,
                videoheadlineCF.distributionId,
            ),
            portMappings: [
                {
                    containerPort: 80,
                    hostPort: 80,
                    protocol: ecs.Protocol.TCP,
                },
            ],
            containerName: 'video-hub',
            logging: ecs.LogDriver.awsLogs({
                streamPrefix: 'ecs',
            }),
            secrets: {
                DATABASE_PASSWORD: ecs.Secret.fromSecretsManager(
                    this.dbSecret,
                    'password'
                ),
                AWS_ACCESS_KEY_ID: ecs.Secret.fromSecretsManager(
                    props.awsConfigSecret,
                    'accessKeyId'
                ),
                AWS_SECRET_ACCESS_KEY: ecs.Secret.fromSecretsManager(
                    props.awsConfigSecret,
                    'secretAccessKey'
                ),
            },
        });
        vhCeleryTaskDefinition.addContainer('vhCelery', {
            image: new ecs.EcrImage(vhEcr, 'latest'),
            environment: taskDefinitionEnvironment(
                this.database.instanceEndpoint.hostname,
                qhubRedisCluster.redisEndpoint
            ),
            command: [
                '/usr/local/bin/celery',
                '-A',
                'video_hub',
                'worker',
                '-l',
                'debug',
                '-Q',
                'default',
            ],
            containerName: 'celery',
            logging: ecs.LogDriver.awsLogs({
                streamPrefix: 'ecs',
            }),
            secrets: {
                DATABASE_PASSWORD: ecs.Secret.fromSecretsManager(
                    this.dbSecret,
                    'password'
                ),
                AWS_ACCESS_KEY_ID: ecs.Secret.fromSecretsManager(
                    props.awsConfigSecret,
                    'accessKeyId'
                ),
                AWS_SECRET_ACCESS_KEY: ecs.Secret.fromSecretsManager(
                    props.awsConfigSecret,
                    'secretAccessKey'
                ),
            },
        });
        vhCeleryTaskDefinition.addContainer('vhCeleryTranscode', {
            image: new ecs.EcrImage(vhEcr, 'latest'),
            environment: taskDefinitionEnvironment(
                this.database.instanceEndpoint.hostname,
                qhubRedisCluster.redisEndpoint
            ),
            command: [
                '/usr/local/bin/celery',
                '-A',
                'video_hub',
                'worker',
                '-l',
                'info',
                '-Q',
                'transcode',
            ],
            containerName: 'celery-transcode',
            logging: ecs.LogDriver.awsLogs({
                streamPrefix: 'ecs',
            }),
            secrets: {
                DATABASE_PASSWORD: ecs.Secret.fromSecretsManager(
                    this.dbSecret,
                    'password'
                ),
                AWS_ACCESS_KEY_ID: ecs.Secret.fromSecretsManager(
                    props.awsConfigSecret,
                    'accessKeyId'
                ),
                AWS_SECRET_ACCESS_KEY: ecs.Secret.fromSecretsManager(
                    props.awsConfigSecret,
                    'secretAccessKey'
                ),
            },
        });
        vhCeleryTaskDefinition.addContainer('vhCeleryBeat', {
            image: new ecs.EcrImage(vhEcr, 'latest'),
            environment: taskDefinitionEnvironment(
                this.database.instanceEndpoint.hostname,
                qhubRedisCluster.redisEndpoint
            ),
            command: [
                '/usr/local/bin/celery',
                '-A',
                'video_hub',
                'beat',
                '-l',
                'info',
                '--pidfile=',
                '--scheduler',
                'django_celery_beat.schedulers:DatabaseScheduler',
            ],
            containerName: 'celery-beat',
            logging: ecs.LogDriver.awsLogs({
                streamPrefix: 'ecs',
            }),
            secrets: {
                DATABASE_PASSWORD: ecs.Secret.fromSecretsManager(
                    this.dbSecret,
                    'password'
                ),
                AWS_ACCESS_KEY_ID: ecs.Secret.fromSecretsManager(
                    props.awsConfigSecret,
                    'accessKeyId'
                ),
                AWS_SECRET_ACCESS_KEY: ecs.Secret.fromSecretsManager(
                    props.awsConfigSecret,
                    'secretAccessKey'
                ),
            },
        });

        // Creation of the Docker image
        const vhImage = isProduction ? 'qualabs/video-headline:latest' : new DockerImageAsset(this, 'VideoHeadlineImage', {
            directory: join(__dirname, '../../'),
            exclude: ['/infrastructure/cdk.out'],
        }).imageUri;

        // Deploying Docker image to the ECR repository
        const vhImageDeploy = new ecrdeploy.ECRDeployment(
            this,
            'VideohealineDockerImage',
            {
                src: new ecrdeploy.DockerImageName(vhImage),
                dest: new ecrdeploy.DockerImageName(
                    vhEcr.repositoryUriForTag('latest')
                ),
            }
        );

        // ECS services
        const vhCeleryService = new ecs.FargateService(
            this,
            'vhCeleryService',
            {
                taskDefinition: vhCeleryTaskDefinition,
                cluster: vhCluster,
                desiredCount: 1,
                securityGroups: [securityGroup],
                enableExecuteCommand: true,
            }
        );
        const videoHubService = new ecs.FargateService(this, 'video-hubService', {
            taskDefinition: videoHubTaskDefinition,
            cluster: vhCluster,
            desiredCount: 1,
            securityGroups: [securityGroup],
            enableExecuteCommand: true,
        });
        securityGroup.connections.allowInternally(ec2.Port.allTraffic(), 'Allow internal connections within the cluster');

        vhCeleryService.node.addDependency(vhImageDeploy);
        videoHubService.node.addDependency(vhImageDeploy);

        // Load Balancer configuration

        if (qhubDevCertArn !== '') {
            // Configuring HTTPS listener if a certificate is provided in aws.ts
            const vhLoadBalancerListenerhttps = vhLoadBalancer.addListener('vhLoadBalancerListener', {
                port: 443,
                open: true,
                protocol: elb.ApplicationProtocol.HTTPS,
                certificates: [
                    elb.ListenerCertificate.fromCertificateManager(
                        aws_certificatemanager.Certificate.fromCertificateArn(
                            this,
                            'videoheadline-cert',
                            qhubDevCertArn
                        )
                    ),
                ],
            });

            vhLoadBalancer.addRedirect({
                sourcePort: 80,
                targetPort: 443,
                open: true,
            });

            vhLoadBalancerListenerhttps.addTargets('vhLoadBalancerTarget', {
                targets: [videoHubService],
                port: 80,
                deregistrationDelay: Duration.seconds(300),
                loadBalancingAlgorithmType:
                    elb.TargetGroupLoadBalancingAlgorithmType.ROUND_ROBIN,
            });
        } else {
            // Configuring HTTP listener if no certificate is provided
            const vhLoadBalancerListenerhttp = vhLoadBalancer.addListener('vhLoadBalancerListener', {
                port: 80,
                open: true,
                protocol: elb.ApplicationProtocol.HTTP,
            });

            vhLoadBalancerListenerhttp.addTargets('vhLoadBalancerTarget', {
                targets: [videoHubService],
                port: 80,
                protocol: elb.ApplicationProtocol.HTTP,
                deregistrationDelay: Duration.seconds(300),
                loadBalancingAlgorithmType:
                    elb.TargetGroupLoadBalancingAlgorithmType.ROUND_ROBIN,
            });
        }
        vhCeleryService.node.addDependency(vhImageDeploy);
        videoHubService.node.addDependency(vhImageDeploy);

    };

    private createVPC() {
        this.vpc = new ec2.Vpc(this, 'VideoheadlineVPC', {
            vpcName: 'VideoheadlineVPC',
            subnetConfiguration: [
                {
                    cidrMask: 24,
                    name: 'VideoheadlineHub/Public1',
                    subnetType: ec2.SubnetType.PUBLIC,
                },
                {
                    cidrMask: 24,
                    name: 'VideoheadlineHub/Public2',
                    subnetType: ec2.SubnetType.PUBLIC,
                },
                {
                    cidrMask: 24,
                    name: 'VideoheadlineHub/Private',
                    subnetType: ec2.SubnetType.PRIVATE_WITH_NAT,
                },
            ],
        });
    };

    private createDB(securityGroup: ec2.SecurityGroup): db.DatabaseInstance {
        const vhDatabase = new db.DatabaseInstance(this, 'VideoheadlineDB', {
            engine: db.DatabaseInstanceEngine.postgres({
                version: engineVersion,
            }),
            vpc: this.vpc,
            databaseName: 'db_video_hub',
            instanceIdentifier: 'videoheadline-db',
            allocatedStorage: 20,
            storageType: storageTypes,
            deletionProtection: false,
            backupRetention: Duration.days(7),
            instanceType: ec2.InstanceType.of(
                ec2.InstanceClass.T3,
                ec2.InstanceSize.MICRO
            ),
            enablePerformanceInsights: true,
            securityGroups: [securityGroup],
        });
        return vhDatabase
    };
}
