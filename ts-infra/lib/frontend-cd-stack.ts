import * as cdk from "@aws-cdk/core"
import * as codebuild from '@aws-cdk/aws-codebuild';
import * as codecommit from '@aws-cdk/aws-codecommit';
import * as iam from "@aws-cdk/aws-iam"
import {BuildSpec} from "@aws-cdk/aws-codebuild";
import * as s3 from "@aws-cdk/aws-s3"
import * as secretsmanager from "@aws-cdk/aws-secretsmanager"

export class CodeBuildFrontend extends cdk.Stack {
    constructor(scope: cdk.Construct, id: string, bucket: string, props?: cdk.StackProps) {
        super(scope, id, props);


        // github source
        const gitHubSource = codebuild.Source.gitHub({
            owner: 'manrodri',
            repo: 'messaging_serverless',
            webhook: true, // optional, default: true if `webhookFilters` were provided, false otherwise
            webhookFilters: [
                codebuild.FilterGroup
                    .inEventOf(codebuild.EventAction.PUSH)
                    .andBranchIs('ts')
            ], // optional, by default all pushes and Pull Requests will trigger a build
        });

        const frontendBucket = s3.Bucket.fromBucketName(this, 'bucket', bucket)

        const buildProject = new codebuild.Project(this, 'MyFirstCodeCommitProject', {
            source: gitHubSource,
            buildSpec: BuildSpec.fromSourceFilename("ts-infra/buildspec.yaml"),
            projectName: "frontendCodeBuildJob",
            environment: {
                buildImage: codebuild.LinuxBuildImage.STANDARD_5_0,
                environmentVariables: {
                    HOSTING_BUCKET: {
                        value: frontendBucket.bucketName,
                        type: codebuild.BuildEnvironmentVariableType.PLAINTEXT
                    }
                }
            }
        });

        buildProject.role?.addToPolicy(new iam.PolicyStatement({actions: ["s3:*"], resources: ["*"]}))


    }
}

