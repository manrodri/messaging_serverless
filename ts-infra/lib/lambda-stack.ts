import * as lambda from "@aws-cdk/aws-lambda"
import * as cdk from "@aws-cdk/core";
import {Bucket} from "@aws-cdk/aws-s3";
import * as path from "path";
import * as iam from '@aws-cdk/aws-iam'
import * as apigateway from "@aws-cdk/aws-apigateway"
import {addCorsOptions} from "./enableCors";
import * as cloudwatch from '@aws-cdk/aws-cloudwatch';
import * as codedeploy from '@aws-cdk/aws-codedeploy'


export class LambdaStack extends cdk.Stack {
    UrlOutput: cdk.CfnOutput;

    constructor(scope: cdk.Construct, id: string, bucket: string, props?: cdk.StackProps) {
        super(scope, id, props);

        cdk.Tags.of(this).add('environment', process.env.SDLC_ENVIRONMENT || 'dev');

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

        const alias = new lambda.Alias(this, 'x', {
            aliasName: 'Current',
            version: fn.currentVersion
        });

        const api = new apigateway.RestApi(
            this,
            'chats',
            {}
        );

        // integrations
        const getConversationHandler =
            new apigateway.LambdaIntegration(alias);

        // resources and methods
        const conversations = api.root.addResource('conversations');
        addCorsOptions(conversations, "*");
        conversations.addMethod('GET', getConversationHandler);
        conversations.addMethod('POST');

        const conversation = conversations.addResource('{conversation_id}');
        addCorsOptions(conversation, "*")
        conversation.addMethod("GET");
        conversation.addMethod("POST");


        this.UrlOutput = new cdk.CfnOutput(this, 'Url', {
            value: api.urlForPath('/conversations')
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

        new codedeploy.LambdaDeploymentGroup(this, 'DeploymentGroup ', {
            alias: alias,
            deploymentConfig: codedeploy.LambdaDeploymentConfig.CANARY_10PERCENT_10MINUTES,
            alarms: [
                failureAlarm
            ]
        });


    }
}


