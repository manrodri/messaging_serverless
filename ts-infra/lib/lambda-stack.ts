import * as lambda from "@aws-cdk/aws-lambda"
import * as cdk from "@aws-cdk/core";
import {Bucket} from "@aws-cdk/aws-s3";
import * as s3 from "@aws-cdk/aws-s3";
import {CfnOutput} from "@aws-cdk/core";
import * as path from "path";

export class LambdaStack extends cdk.Stack {
  constructor(scope: cdk.Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    const fn = new lambda.Function(this, 'MyFunction', {
  runtime: lambda.Runtime.NODEJS_14_X,
  handler: 'index.handler',
  code: lambda.Code.fromAsset(path.join(__dirname, 'lambda-handler/proxy')),
});

  }
}


