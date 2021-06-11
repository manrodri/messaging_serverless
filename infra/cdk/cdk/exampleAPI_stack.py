# Example automatically generated. See https://github.com/aws/jsii/issues/826
from aws_cdk.core import App, CfnOutput, NestedStack, NestedStackProps, Stack
from constructs import Construct
from aws_cdk.aws_apigateway import Deployment, Method, MockIntegration, PassthroughBehavior, RestApi, Stage, MethodResponse

#
# This file showcases how to split up a RestApi's Resources and Methods across nested stacks.
#
# The root stack 'RootStack' first defines a RestApi.
# Two nested stacks BooksStack and PetsStack, create corresponding Resources '/books' and '/pets'.
# They are then deployed to a 'prod' Stage via a third nested stack - DeployStack.
#
# To verify this worked, go to the APIGateway
#


class RootStack(Stack):
    def __init__(self, scope):
        super().__init__(scope, "integ-restapi-import-RootStack")

        rest_api = RestApi(self, "RestApi",
                           deploy=False
                           )
        rest_api.root.add_method("ANY")

        pets_stack = PetsStack(self,
                               rest_api_id=rest_api.rest_api_id,
                               root_resource_id=rest_api.rest_api_root_resource_id
                               )
        books_stack = BooksStack(self,
                                 rest_api_id=rest_api.rest_api_id,
                                 root_resource_id=rest_api.rest_api_root_resource_id
                                 )
        # DeployStack(self,
        #             rest_api_id=rest_api.rest_api_id,
        #             methods=[(SpreadElement ...petsStack.methods pets_stack.methods), (SpreadElement ...booksStack.methods
        #                                             books_stack.methods)]
        #             )

        CfnOutput(self, "PetsURL",
                  value=f"https://{restApi.restApiId}.execute-api.{this.region}.amazonaws.com/prod/pets"
                  )

        CfnOutput(self, "BooksURL",
                  value=f"https://{restApi.restApiId}.execute-api.{this.region}.amazonaws.com/prod/books"
                  )


class PetsStack(NestedStack):

    def __init__(self, scope, *, restApiId, rootResourceId, parameters=None, timeout=None, notificationArns=None, removalPolicy=None):
        super().__init__(scope, "integ-restapi-import-PetsStack", restApiId=restApiId, rootResourceId=rootResourceId,
                         parameters=parameters, timeout=timeout, notificationArns=notificationArns, removalPolicy=removalPolicy)

        api = RestApi.from_rest_api_attributes(self, "RestApi",
                                               rest_api_id=restApiId,
                                               root_resource_id=rootResourceId
                                               )

        method = api.root.add_resource("pets").add_method("GET", MockIntegration({
            "integration_responses": [{
                "status_code": "200"
            }],
            "passthrough_behavior": PassthroughBehavior.NEVER,
            "request_templates": {
                "application/json": "{ \"statusCode\": 200 }"
            }
        }),
            method_responses=[MethodResponse(status_code="200")]
        )

        self.methods.push(method)


class BooksStack(NestedStack):

    def __init__(self, scope, *, restApiId, rootResourceId, parameters=None, timeout=None, notificationArns=None, removalPolicy=None):
        super().__init__(scope, "integ-restapi-import-BooksStack", restApiId=restApiId, rootResourceId=rootResourceId,
                         parameters=parameters, timeout=timeout, notificationArns=notificationArns, removalPolicy=removalPolicy)

        api = RestApi.from_rest_api_attributes(self, "RestApi",
                                               rest_api_id=rest_api_id,
                                               root_resource_id=root_resource_id
                                               )

        method = api.root.add_resource("books").add_method("GET", MockIntegration({
            "integration_responses": [{
                "status_code": "200"
            }],
            "passthrough_behavior": PassthroughBehavior.NEVER,
            "request_templates": {
                "application/json": "{ "statusCode": 200 }"
            }
        }),
            method_responses=[MethodResponse(status_code="200")]
        )

        self.methods.push(method)


class DeployStack(NestedStack):
    def __init__(self, scope, *, restApiId, methods=None, parameters=None, timeout=None, notificationArns=None, removalPolicy=None):
        super().__init__(scope, "integ-restapi-import-DeployStack", restApiId=restApiId, methods=methods,
                         parameters=parameters, timeout=timeout, notificationArns=notificationArns, removalPolicy=removalPolicy)

        deployment = Deployment(self, "Deployment",
                                api=RestApi.from_rest_api_id(
                                    self, "RestApi", rest_api_id)
                                )
        (methods ?? []).for_each((method)=> deployment.node.addDependency(method))
        Stage(self, "Stage", deployment=deployment)
