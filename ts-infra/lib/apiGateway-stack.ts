import * as cdk from "@aws-cdk/core";
import * as lambda from "@aws-cdk/aws-lambda"
import * as apigateway from "@aws-cdk/aws-apigateway";
import {addCorsOptions} from "./enableCors";

export class ApiGatewayStack extends cdk.Stack {
     stgUrlOutput: cdk.CfnOutput;

    constructor(scope: cdk.Construct, id: string, fn: lambda.Alias, props?: cdk.StackProps) {
        super(scope, id, props);



        const api = new apigateway.RestApi(
            this,
            'newChats',
        );

        // integrations
        const getConversationHandlerStg =
            new apigateway.LambdaIntegration(fn);

        // resources and methods
        const conversations = api.root.addResource('conversations');
        addCorsOptions(conversations, "*");
        conversations.addMethod('GET', getConversationHandlerStg);
        conversations.addMethod('POST');

        const conversation = conversations.addResource('{conversation_id}');
        addCorsOptions(conversation, "*")
        conversation.addMethod("GET");
        conversation.addMethod("POST");


        this.stgUrlOutput = new cdk.CfnOutput(this, 'stgUrl', {
            value: api.urlForPath('/conversations')
        })


        const stgDeployment = new apigateway.Deployment(this, 'stgDeployment', {
            api: api,
            description: "stg deployment"

        })

        const stgStage = new apigateway.Stage(this, 'stgStage', {
            deployment: stgDeployment,
            stageName: 'stg'
        })

        const prodDeployment = new apigateway.Deployment(this, 'prodDeployment', {
            api: api,
            description: "prod deployment",

        })

        const prodStage = new apigateway.Stage(this, 'prodStage', {
            deployment: prodDeployment,
            stageName: 'prod',

        })

        api.deploymentStage = stgStage






    }
}
