from aws_cdk import (
    aws_lambda as lb,
    aws_apigateway as apigw,
    aws_s3 as s3,
    aws_dynamodb as dynamodb,
    core,
)


class LambdaStack(core.Stack):

    def __init__(
            self,
            scope: core.Construct, id: str,
            frontendBucket,
            conversations_table: dynamodb.Table,
            messages_table: dynamodb.Table,
            **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        webhostingbucket = s3.Bucket.from_bucket_name(self, 'webhosting-bucket',
                                                      bucket_name=frontendBucket)

        lambda_function = lb.Function(self, 'chat-proxy',
                                      runtime=lb.Runtime.NODEJS_12_X,
                                      code=lb.Code.asset('./lambda'),
                                      handler='Chat-Proxy.handler'
                                      )

        api_gateway = apigw.LambdaRestApi(self, 'chat-api',
                                          handler=lambda_function,
                                          rest_api_name='chat-api',
                                          default_cors_preflight_options={
                                              "allow_origins": apigw.Cors.ALL_ORIGINS,
                                              "allow_methods": apigw.Cors.ALL_ORIGINS,
                                          }
                                          )

        webhostingbucket.grant_read(lambda_function)
        conversations_table.grant(lambda_function, "dynamodb:*")
        messages_table.grant(lambda_function, "dynamodb:*")
