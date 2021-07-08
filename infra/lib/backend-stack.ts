import * as cdk from '@aws-cdk/core';
import {Code, Function, Runtime} from '@aws-cdk/aws-lambda';
import {Bucket} from "@aws-cdk/aws-s3"

export class BackendStack extends cdk.Stack {
    constructor(scope: cdk.App, id: string, bucket: string, props?: cdk.StackProps) {
        super(scope, id, props);

        cdk.Tags.of(this).add('environment', process.env.SDLC_ENVIRONMENT || 'dev');
        const frontendBucket = Bucket.fromBucketName(this, 'bucket', bucket)

        const proxyFunction = new Function(this, "proxyFunction", {
            runtime: Runtime.NODEJS_14_X,
            handler: 'app.handler',
            code: Code.fromAsset('src/proxy'),
            environment: {
                'BUCKET_NAME': frontendBucket.bucketName
            }
        })


    }
}
