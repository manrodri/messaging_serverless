import * as cdk from '@aws-cdk/core';
import {Code, Function, Runtime, Alias} from '@aws-cdk/aws-lambda';
import {Bucket} from "@aws-cdk/aws-s3"
import * as iam from "@aws-cdk/aws-iam"
import {RestApi, LambdaIntegration} from "@aws-cdk/aws-apigateway";
import {addCorsOptions} from "./enableCors";
import {CfnOutput} from "@aws-cdk/core";
import * as cloudwatch from "@aws-cdk/aws-cloudwatch"

export class BackendStack extends cdk.Stack {
    public ConversationsUrlOutput: CfnOutput;
    public ConversationUrlOutput: CfnOutput
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

        proxyFunction.role?.addManagedPolicy(iam.ManagedPolicy.fromManagedPolicyArn(
            this,
            "mypolicy",
            'arn:aws:iam::aws:policy/AmazonS3FullAccess'))

        const alias = new Alias(this, 'x', {
            aliasName: 'Current',
            version: proxyFunction.currentVersion
        });

        const api = new RestApi(
            this,
            'chats',
            {}
        );

        // integrations
        const getConversationHandler =
            new LambdaIntegration(alias);

        // resources and methods
        const conversations = api.root.addResource('conversations');
        addCorsOptions(conversations, "*");
        conversations.addMethod('GET', getConversationHandler);
        conversations.addMethod('POST');

        const conversation = conversations.addResource('{conversation_id}');
        addCorsOptions(conversation, "*")
        conversation.addMethod("GET", getConversationHandler);
        conversation.addMethod("POST", getConversationHandler)

        this.ConversationsUrlOutput = new cdk.CfnOutput(this, 'ConversationsUrl', {
            value: api.urlForPath('/conversations')
        })

        this.ConversationUrlOutput = new cdk.CfnOutput(this, 'ConversationUrl', {
            value: api.urlForPath('/conversation')
        })

        // CloudWatch
        const apiGateway5xx = new cloudwatch.Metric({
            metricName: '5XXError',
            namespace: 'AWS/ApiGateway',
            dimensions: {
                ApiName: 'chats'
            },
            statistic: 'Sum',
        });
        const failureAlarm = new cloudwatch.Alarm(this, 'RollbackAlarm', {
            metric: apiGateway5xx,
            threshold: 1,
            evaluationPeriods: 1,
        });

    }
}
