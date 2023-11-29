import { CfnCacheCluster } from 'aws-cdk-lib/aws-elasticache';
import { Construct } from 'constructs';
import { aws_ec2 as ec2, aws_elasticache as elasticache } from 'aws-cdk-lib';

export interface RedisClusterProps {
    vpc: ec2.IVpc;
    sg: ec2.SecurityGroup;
}
export class RedisCluster extends Construct {
    readonly redisEndpoint: string;
    constructor(scope: Construct, id: string, props: RedisClusterProps) {
        super(scope, id);

        // Define a group for telling Elasticache which subnets to put cache nodes in.
        const subnetGroup = new elasticache.CfnSubnetGroup(this, 'qhub-redis', {
            description: `List of subnets used for redis cache`,
            subnetIds: props.vpc.privateSubnets.map(
                (subnet) => subnet.subnetId
            ),
        });

        // Define construct contents here
        const redis = new CfnCacheCluster(this, 'redis-cluster', {
            cacheNodeType: 'cache.t2.micro',
            engine: 'redis',
            numCacheNodes: 1,

            // the properties below are optional
            azMode: 'single-az',
            // cacheSecurityGroupNames: [props.sg.securityGroupId],
            cacheSubnetGroupName: subnetGroup.ref,
            clusterName: 'redis',
            port: 6379,
            vpcSecurityGroupIds: [props.sg.securityGroupId],
            preferredMaintenanceWindow: 'sun:06:00-sun:07:00',
        });
        this.redisEndpoint = `${redis.attrRedisEndpointAddress}:${redis.port}`;
    }
}
