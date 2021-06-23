import { CfnOutput, Construct, Stage, StageProps } from '@aws-cdk/core';
import { LambdaStack } from './lambda-stack';
import { Bucket } from "@aws-cdk/aws-s3";

/**
 * Deployable unit of web service app
 */
export class CdkpipelinesDemoStage extends Stage {
  public readonly urlOutput: CfnOutput;

  constructor(scope: Construct, id: string, bucketName: string, props?: StageProps) {
    super(scope, id, props);

    const service = new LambdaStack(this, 'WebService', bucketName);

    // Expose CdkpipelinesDemoStack's output one level higher
    this.urlOutput = service.UrlOutput;
  }
}