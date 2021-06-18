import * as cdk from "@aws-cdk/core"
import * as codebuild from '@aws-cdk/aws-codebuild';
import * as codecommit from '@aws-cdk/aws-codecommit';
import * as iam from "@aws-cdk/aws-iam"
import {BuildSpec} from "@aws-cdk/aws-codebuild";
import * as s3 from "@aws-cdk/aws-s3"

export class CodeBuildFrontend extends cdk.Stack {
    constructor(scope: cdk.Construct, id: string, bucket: string, props?: cdk.StackProps) {
        super(scope, id, props);

        // The code that defines your stack goes here
        const repository = codecommit.Repository.fromRepositoryName(this, 'repo', "messaging_serverless")
        const source = codebuild.Source.codeCommit({repository: repository, branchOrRef: "ts"})

        const frontendBucket = s3.Bucket.fromBucketName(this, 'bucket', bucket )

        const buildProject = new codebuild.Project(this, 'MyFirstCodeCommitProject', {
            source: source,
            buildSpec: BuildSpec.fromSourceFilename("ts-infra/buildspec.yaml"),
            projectName: "frontendCodeBuildJob",
            environment: {
                buildImage: codebuild.LinuxBuildImage.STANDARD_5_0,
                environmentVariables: {
                  HOSTING_BUCKET: {
                      value: frontendBucket,
                      type: codebuild.BuildEnvironmentVariableType.PLAINTEXT
                  }
                }
            }
        });

        buildProject.role?.addToPolicy(new iam.PolicyStatement({actions:["s3:*"], resources:["*"]}))


    }
}

