from aws_cdk import (
    aws_lambda as lb,
    aws_apigateway as apigw,
    aws_s3 as s3,
    aws_dynamodb as dynamodb,
    aws_cognito as cognito,
    aws_iam as iam,
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

        cognito_user_pool = cognito.UserPool.from_user_pool_id(
            self,
            'cognito-user-pool',
            user_pool_id='eu-west-1_8M8dkG2Tq'
        )

        lambda_function = lb.Function(self, 'chat-proxy',
                                      runtime=lb.Runtime.NODEJS_12_X,
                                      code=lb.Code.asset('./lambda'),
                                      handler='Chat-Proxy.handler'
                                      )

        self.lb_conversations_get = lb.Function(
            self,
            'lambda-conversations-get',
            runtime=lb.Runtime.NODEJS_12_X,
            code=lb.Code.asset('./lambda/conversations-get'),
            handler='Chat-Conversations-Get.handler'

        )

        self.lb_messages_get = lb.Function(
            self,
            'lambda-messages-get',
            runtime=lb.Runtime.NODEJS_12_X,
            code=lb.Code.asset('./lambda/messages-get'),
            handler='Chat-Messages-Get.handler'
        )

        self.lb_messages_post = lb.Function(
            self,
            'lambda-messages-post',
            code=lb.Code.asset('./lambda/messages-post'),
            handler='Chat-Messages-Post.handler',
            runtime=lb.Runtime.NODEJS_12_X
        )

        self.lb_user_get = lb.Function(
            self,
            'lambda-user-get',
            runtime=lb.Runtime.NODEJS_12_X,
            code=lb.Code.asset('./lambda/users-get'),
            handler='Chat-User-Get.handler',
            environment={
                'USER_POOL_ID': cognito_user_pool.user_pool_id
            }
        )

        cognito_arn = cognito_user_pool.user_pool_arn
        cognito_statement = iam.PolicyStatement()
        cognito_statement.add_resources(cognito_arn)
        cognito_statement.add_actions('cognito-idp:ListUsers')


        conversations_table.grant(self.lb_messages_post, "dynamodb:*")
        messages_table.grant(self.lb_messages_post, "dynamodb:*")

        conversations_table.grant(self.lb_messages_get, "dynamodb:*")
        messages_table.grant(self.lb_messages_get, "dynamodb:*")

        conversations_table.grant(self.lb_conversations_get, "dynamodb:*")
        messages_table.grant(self.lb_conversations_get, "dynamodb:*")

        conversations_table.grant(lambda_function, "dynamodb:*")
        messages_table.grant(lambda_function, "dynamodb:*")

        self.lb_user_get.role.add_to_policy(cognito_statement)
