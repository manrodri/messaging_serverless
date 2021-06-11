#!/usr/bin/env python3
import os
from aws_cdk import core

from cdk.CloudFront_stack import CDNStack
from cdk.s3_stack import S3Stack
from cdk.DNS_stack import DnsStack
from cdk.lambda_stack import LambdaStack
from cdk.dynamodb_stack import DynamodbStack
from cdk.frontend_pipeline_stack import CodePipelineFrontendStack
from cdk.ApiGateway_stack import ApiCorsLambdaStack
from cdk.acm_stack import ACMStack
from cdk.ApiLambdaIntegration_stack import ApiLambdaStack


environment = {
    "region": 'eu-west-1',
    'account': '423754860743'
}

app = core.App()
s3_stack = S3Stack(app, "CdkStack", env=environment)

acm_stack = ACMStack(
    app,
    'AcmStack',
    env={"account": environment['account'], "region": "us-east-1"})

cdn_stack = CDNStack(
    app,
    'cdnStack',
    s3bucket=core.Fn.import_value('frontend-bucket'),
    env=environment
)

dns_stack = DnsStack(app,
                     'DNSStack',
                     cdnid=cdn_stack.cdn_id,
                     env=environment
                     )

dynamodb_stack = DynamodbStack(app, 'dynamodbStack', env=environment)

lambda_stack = LambdaStack(app,
                           'LambdaStack',
                           frontendBucket=core.Fn.import_value(
                               'frontend-bucket'),
                           conversations_table=dynamodb_stack.chat_conversations_table,
                           messages_table=dynamodb_stack.chat_messages_table,
                           env=environment
                           )

frontend_pipeline = CodePipelineFrontendStack(app,
                                              'FrontendPipelineStack',
                                              webhostingbucket=core.Fn.import_value(
                                                  'frontend-bucket'),
                                              env=environment
                                              )

apiGateway = ApiCorsLambdaStack(app,
                                'ApigatewayStack',
                                conversations_lambda=lambda_stack.lb_conversations_get,
                                env=environment)

apiLambdaIntegration = ApiLambdaStack(
    app,
    'apigwIntegration',
    env=environment
)

app.synth()
