from aws_cdk import (
    aws_dynamodb as dynamodb,
    aws_ssm as ssm,
    core as cdk
)


class DynamodbStack(cdk.Stack):

    def __init__(self, scope: cdk.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        prj_name = self.node.try_get_context("project_name")
        env_name = self.node.try_get_context("env")
        domain_name = self.node.try_get_context("domain_name")

        self.chat_messages_table = dynamodb.Table(self, "messages_table",
                               table_name= 'Chat-Messages',
                               partition_key=dynamodb.Attribute(
                                   name="ConversationId",
                                   type=dynamodb.AttributeType.STRING),
                               sort_key=dynamodb.Attribute(
                                   name="Timestamp",
                                   type=dynamodb.AttributeType.NUMBER
                               ),
                               read_capacity=1,

                               write_capacity=1,
                               removal_policy=cdk.RemovalPolicy.DESTROY,
                               )

        self.chat_conversations_table = dynamodb.Table(
            self,
            "conversations_table",
            table_name='Chat-Conversations',
            partition_key=dynamodb.Attribute(
                name="ConversationId",
                type=dynamodb.AttributeType.STRING
            ),
            sort_key=dynamodb.Attribute(
                name='Username',
                type=dynamodb.AttributeType.STRING
            ),
            read_capacity=1,
            write_capacity=1,
            removal_policy=cdk.RemovalPolicy.DESTROY,
        )
        self.chat_conversations_table.add_global_secondary_index(

            partition_key=dynamodb.Attribute(
                name='Username',
                type=dynamodb.AttributeType.STRING
            ),
            sort_key=dynamodb.Attribute(
                name='ConversationId',
                type=dynamodb.AttributeType.STRING
            ),
            read_capacity=1,
            write_capacity=1,
            index_name='secondary_index'
        )


        ssm.StringParameter(self, 'messages-table-arn',
                            parameter_name='/' + env_name + '/messages_table_arn',
                            string_value=self.chat_messages_table.table_arn
                            )

        ssm.StringParameter(self, 'conversations-table-arn',
                            parameter_name='/' + env_name + '/conversations_table_arn',
                            string_value=self.chat_conversations_table.table_arn
                            )
