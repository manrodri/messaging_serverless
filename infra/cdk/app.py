#!/usr/bin/env python3
import os
from aws_cdk import core

from cdk.s3_stack import S3Stack
from cdk.DNS_stack import DnsStack
from cdk.lambda_stack import LambdaStack
from cdk.dynamodb_stack import DynamodbStack
from cdk.frontend_pipeline_stack import CodePipelineFrontendStack
from cdk.ApiGateway_stack import ApiCorsLambdaStack

environment = core.Environment(
    account=os.environ.get('CDK_DEFAULT_ACCOUNT'),
    region=os.environ.get('CDK_DEFAULT_REGION')
)

app = core.App()
s3_stack = S3Stack(app, "CdkStack", env=environment)
dns_stack = DnsStack(app,
                     'DNSStack',
                     frontendBucket=core.Fn.import_value('frontend-bucket'),
                     env=environment
                     )

dynamodb_stack = DynamodbStack(app, 'dynamodbStack', env=environment)


lambda_stack = LambdaStack(app,
                           'LambdaStack',
                            frontendBucket=core.Fn.import_value('frontend-bucket'),
                            conversations_table=dynamodb_stack.chat_conversations_table,
                            messages_table=dynamodb_stack.chat_messages_table,
                           env=environment
                           )

frontend_pipeline = CodePipelineFrontendStack(app,
                                              'FrontendPipelineStack',
                                              webhostingbucket=core.Fn.import_value('frontend-bucket'),
                                              env=environment
                                              )

apiGateway = ApiCorsLambdaStack(app,
                                'ApigatewayStack',
                                conversations_lambda=lambda_stack.lb_conversations_get ,
                                env=environment)

app.synth()
