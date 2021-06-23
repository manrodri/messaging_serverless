import * as lambda from "@aws-cdk/aws-lambda"
import * as cdk from "@aws-cdk/core";
import {Bucket} from "@aws-cdk/aws-s3";
import * as path from "path";
import * as iam from '@aws-cdk/aws-iam'
import * as apigateway from "@aws-cdk/aws-apigateway"

export class LambdaStack extends cdk.Stack {
    UrlOutput: cdk.CfnOutput;
    constructor(scope: cdk.Construct, id: string, bucket: string, props?: cdk.StackProps) {
        super(scope, id, props);

        const frontendBucket = Bucket.fromBucketName(this, 'bucket', bucket)

        const fn = new lambda.Function(this, 'MyFunction', {
            runtime: lambda.Runtime.NODEJS_14_X,
            handler: 'index.handler',
            code: lambda.Code.fromAsset(path.join(__dirname, '../lambda/proxy')),
            tracing: lambda.Tracing.ACTIVE,
            environment: {
                "BUCKET_NAME": frontendBucket.bucketName
            }
        });

        fn.role?.addManagedPolicy(iam.ManagedPolicy.fromManagedPolicyArn(
            this,
            "mypolicy",
            'arn:aws:iam::aws:policy/AmazonS3FullAccess'))

        const api = new apigateway.RestApi(
            this,
            'myapi',
            {}
        );

        // integrations
        const getConversationHandler =
            new apigateway.LambdaIntegration(fn.currentVersion);

        // resources and methods
        const conversations = api.root.addResource('conversations');
        conversations.addMethod('GET', getConversationHandler);
        conversations.addMethod('POST');
        const conversation = conversations.addResource('{conversation_id}');
        conversation.addMethod("GET");
        conversation.addMethod("POST");


        this.UrlOutput = new cdk.CfnOutput(this, 'Url', {
            value: api.urlForPath('/conversations')
        })


    }
}


