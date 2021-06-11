import json

from aws_cdk import (
    core,
    aws_lambda as lb,
    aws_apigateway as apigw,
    aws_ssm as ssm
)


class ApiLambdaStack(core.Stack):

    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        prj_name = self.node.try_get_context("project_name")
        env_name = self.node.try_get_context("env")

        fn = lb.Function(
            self,
            "lambdaFunction",
            runtime=lb.Runtime.PYTHON_3_7,
            code=lb.Code.asset('./lambda'),
            handler='hello.handler'

        )

        base_api = apigw.RestApi(
            self,
            'lambdaIntegrationApi',
        )

        conversation_get_model = apigw.Model(
            self,
            'conversationsGetModel',
            rest_api=base_api,
            schema={
                "schema": apigw.JsonSchemaVersion.DRAFT4,
                "title": "converstaionGetResponse",
                "type": apigw.JsonSchemaType.OBJECT,
                "properties": {
                    "state": {"type": apigw.JsonSchemaType.OBJECT,
                              "properties": {
                                  "foo": {
                                      "type": apigw.JsonSchemaType.STRING
                                  }
                              }
                              },
                    "greeting": {"type": apigw.JsonSchemaType.STRING}
                }
            },
            model_name='conversationsGet'
        )

        error_response_model = apigw.Model(
            self,
            'errorModel',
            rest_api=base_api,
            schema={
                "schema": apigw.JsonSchemaVersion.DRAFT4,
                "title": "errorResponse",
                "type": apigw.JsonSchemaType.OBJECT,
                "properties": {
                    "state": {"type": apigw.JsonSchemaType.STRING},
                    "message": {"type": apigw.JsonSchemaType.STRING}
                }
            }
        )

        # integration_response = apigw.IntegrationResponse(

        # )

        method_response = apigw.MethodResponse(
            status_code="200",
            response_models={
                "application/json": conversation_get_model
            },
            response_parameters={
                "method.response.header._content-_type": True,
                "method.response.header._access-_control-_allow-_origin": True,
                "method.response.header._access-_control-_allow-_credentials": True
            },


        )

        template = {
            "stage": "$context.stage",
            "request_id": "$context.requestId",
            "api_id": "$context.apiId",
            "resource_path": "$context.resourcePath",
            "resource_id": "$context.resourceId",
            "http_method": "$context.httpMethod",
            "source_ip": "$context.identity.sourceIp",
            "user-agent": "$context.identity.userAgent",
            "account_id": "$context.identity.accountId",
            "api_key": "$context.identity.apiKey",
            "caller": "$context.identity.caller",
            "user": "$context.identity.user",
            "user_arn": "$context.identity.userArn"
        }

        integration_response = apigw.IntegrationResponse(
            status_code="200",
            response_parameters={
                # We can map response parameters
                # - Destination parameters (the key) are the response parameters (used in mappings)
                # - Source parameters (the value) are the integration response parameters or expressions
                "method.response.header._content-_type": "'application/json'",
                "method.response.header._access-_control-_allow-_origin": "'*'",
                "method.response.header._access-_control-_allow-_credentials": "'true'"
            },
            response_templates={
                # This template takes the "message" result from the Lambda function, and embeds it in a JSON response
                # Check https://docs.aws.amazon.com/apigateway/latest/developerguide/api-gateway-mapping-template-reference.html
                "application/json": json.dumps(template)
            },

        )

        # JSON.stringify(state="error", message="$util.escapeJavaScript($input.path('$.errorMessage'))")

        conversation_resource = base_api.root.add_resource('conversations')
        conversation_resource.add_method(
            'GET',
            apigw.LambdaIntegration(
                fn,
                proxy=False,
                integration_responses=[
                    integration_response,
                ]
            ),
            request_parameters={
                "method.request.querystring.who": True
            },
            request_validator_options={
                "request_validator_name": "test-validator",
                "validate_request_body": True,
                "validate_request_parameters": False
            },
            method_responses=[
                method_response,
            ],



        )
        self.add_cors_options(conversation_resource)

        api_prod_url = ssm.StringParameter(
            self,
            'api_prod_url',
            parameter_name=f"/{env_name}/api_url{prj_name}",
            string_value=base_api.url
        )

    def add_cors_options(self, apigw_resource):
        apigw_resource.add_method('OPTIONS', apigw.MockIntegration(
            integration_responses=[{
                'statusCode': '200',
                'responseParameters': {
                    'method.response.header.Access-Control-Allow-Headers': "'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token'",
                    'method.response.header.Access-Control-Allow-Origin': "'*'",
                    'method.response.header.Access-Control-Allow-Methods': "'GET,OPTIONS'"
                }
            }
            ],
            passthrough_behavior=apigw.PassthroughBehavior.WHEN_NO_MATCH,
            request_templates={"application/json": "{\"statusCode\":200}"}
        ),
            method_responses=[{
                'statusCode': '200',
                'responseParameters': {
                    'method.response.header.Access-Control-Allow-Headers': True,
                    'method.response.header.Access-Control-Allow-Methods': True,
                    'method.response.header.Access-Control-Allow-Origin': True,
                }
            }
        ],
        )
