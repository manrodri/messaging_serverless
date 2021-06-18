import * as cdk from '@aws-cdk/core';
import {Bucket} from '@aws-cdk/aws-s3'
import * as s3 from "@aws-cdk/aws-s3"
import {CfnOutput} from "@aws-cdk/core"


export class S3Stack extends cdk.Stack {
  constructor(scope: cdk.Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    // The code that defines your stack goes here
    const bucket = new Bucket(this, 'frontendBucket', {
      bucketName:"ts.soydecai.xyz",
      removalPolicy: cdk.RemovalPolicy.DESTROY,
      accessControl: s3.BucketAccessControl.BUCKET_OWNER_FULL_CONTROL,
      websiteIndexDocument:'index.html',
      publicReadAccess: true
    })

    new CfnOutput(
        this,
        'frontEndBucket',
        {
          value:bucket.bucketName,
          exportName: "frontendBucket"
        }
    )

  }
}
