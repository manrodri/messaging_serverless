from aws_cdk import (
    core,
    aws_lambda as _lambda,
    aws_apigateway as _apigw
)


class ApiCorsLambdaStack(core.Stack):

    def __init__(self, scope: core.Construct, id: str, conversations_lambda: _lambda.Function, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        base_api = _apigw.RestApi(self, 'ApiGatewayWithCors',
                                  rest_api_name='ApiGatewayWithCors')

        example_entity = base_api.root.add_resource('conversations')
        example_entity_lambda_integration = _apigw.LambdaIntegration(
            conversations_lambda, proxy=False,
        )

        example_entity.add_method('GET', example_entity_lambda_integration,
        
                                  method_responses=[
                                      _apigw.MethodResponse(status_code="200"),
                                      _apigw.MethodResponse(status_code="204")],

                                  )

        # self.add_cors_options(example_entity)

    def add_cors_options(self, apigw_resource):
        apigw_resource.add_method('OPTIONS', _apigw.MockIntegration(
            integration_responses=[{
                'statusCode': '200',
                'responseParameters': {
                    'method.response.header.Access-Control-Allow-Headers': "'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token'",
                    'method.response.header.Access-Control-Allow-Origin': "'*'",
                    'method.response.header.Access-Control-Allow-Methods': "'GET,OPTIONS'"
                }
            }
            ],
            passthrough_behavior=_apigw.PassthroughBehavior.WHEN_NO_MATCH,
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
