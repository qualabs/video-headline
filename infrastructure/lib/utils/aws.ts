export function defaultTags(): Object {
    return {
        Product: 'videoheadline-opensource',
        Customer: 'Shared',
        CreatedBy: 'some@email.com',
        SystemGUID: '51d6c220-1d2a-4802-bea5-a836b1ae69ff',
    };
}

export function taskDefinitionEnvironment(
    dbHost: string,
    redisHost: string,
): { [key: string]: string } {
    return {
        CONN_MAX_AGE: '0',
        DATABASE_HOST: dbHost,
        DATABASE_USER: 'postgres',
        REDIS_HOST: `redis://${redisHost}`,
    };
}

export function videoHubtaskDefinitionEnvironment(
    dbHost: string,
    redisHost: string,
    mediaconvertRoleArn: string,
    mediaLiveRoleArn: string,
    cloudfrontDns: string,
    cloudfrontId: string,
): { [key: string]: string } {
    return {
        CONN_MAX_AGE: '0',
        DATABASE_HOST: dbHost,
        DATABASE_USER: 'postgres',
        REDIS_HOST: `redis://${redisHost}`,
        AWS_MEDIA_CONVERT_ROLE: mediaconvertRoleArn,
        AWS_MEDIA_LIVE_ROLE: mediaLiveRoleArn,
        BASE_URL: `https://${cloudfrontDns}/`,
        CLOUDFRONT_ID: cloudfrontId,
    };
}

export const qhubDevCertArn: string = '';
