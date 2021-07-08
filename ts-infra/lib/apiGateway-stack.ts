import * as cdk from '@aws-cdk/core';
import * as apigw from '@aws-cdk/aws-apigateway';
import * as lambda from '@aws-cdk/aws-lambda';
import { ServicePrincipal } from '@aws-cdk/aws-iam';
import * as path from "path";

export class ApigwDemoStack extends cdk.Stack {
  constructor(scope: cdk.Construct, id: string, deployment_env: string, props?: cdk.StackProps) {
    super(scope, id, props);

    const env = deployment_env

    // First, create a test lambda
    const myLambda = new lambda.Function(this, 'my_lambda', {
      runtime: lambda.Runtime.NODEJS_14_X,
      code: lambda.Code.fromAsset(path.join(__dirname, '../lambda/proxy')),
      handler: 'test.handler'
    });

    // IMPORTANT: Lambda grant invoke to APIGateway
    myLambda.grantInvoke(new ServicePrincipal('apigateway.amazonaws.com'));

    // Then, create the API construct, integrate with lambda
    const api = new apigw.RestApi(this, 'my_api', { deploy: false });
    const integration = new apigw.LambdaIntegration(myLambda);
    api.root.addMethod('ANY', integration)

    // Then create an explicit Deployment construct
    const deployment  = new apigw.Deployment(this, 'my_deployment', { api });

    api.deploymentStage = new apigw.Stage(this, `${env}_stage`, {deployment, stageName: `${env}`})
  }
}