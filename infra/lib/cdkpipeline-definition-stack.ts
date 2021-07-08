import * as codepipeline from '@aws-cdk/aws-codepipeline';
import * as codepipeline_actions from '@aws-cdk/aws-codepipeline-actions';
import * as cdk from '@aws-cdk/core';
import {Construct, Stack, StackProps} from '@aws-cdk/core';
import * as codebuild from '@aws-cdk/aws-codebuild';
import {BuildSpec} from '@aws-cdk/aws-codebuild';
import * as iam from "@aws-cdk/aws-iam"
import * as s3 from "@aws-cdk/aws-s3"

export class messagingAppPipelineStack extends Stack {
    constructor(scope: Construct, id: string, bucket: string, props?: StackProps) {
        super(scope, id, props);

        // artifacts buckets
        const sourceArtifact = new codepipeline.Artifact();
        const frontendArtifact = new codepipeline.Artifact();
        const backendArtifact = new codepipeline.Artifact();

        // source action
        const gitHubToken = cdk.SecretValue.secretsManager('remoteRepositorieKeys', {
            jsonField: 'GitHub_key'
        })

        const sourceAction = new codepipeline_actions.GitHubSourceAction({
            actionName: 'GitHub',
            output: sourceArtifact,
            oauthToken: gitHubToken,
            owner: 'manrodri',
            repo: 'messaging_serverless',
            branch: 'ts'
        })

        // frontend stage
        const frontendBucket = s3.Bucket.fromBucketName(this, 'bucket', bucket)
        const frontendProject = new codebuild.PipelineProject(this, 'MyProject',{
            buildSpec: BuildSpec.fromSourceFilename("infra/buildspec.yaml"),
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

        frontendProject.role?.addToPolicy(new iam.PolicyStatement({actions: ["s3:*"], resources: ["*"]}))

        const frontendAction = new codepipeline_actions.CodeBuildAction({
            actionName: 'CodeBuild',
            project: frontendProject,
            input: sourceArtifact,
            outputs: [frontendArtifact] // optional
        });

        // backend stage
        const backendProject = new codebuild.PipelineProject(this, 'backendDeployProject',{
            buildSpec: BuildSpec.fromSourceFilename('infra/backendDeployBuildSpec.yaml'),
            environment: {
                buildImage: codebuild.LinuxBuildImage.STANDARD_5_0,
                environmentVariables: {
                    HOSTING_BUCKET: {
                        value: frontendBucket.bucketName,
                        type: codebuild.BuildEnvironmentVariableType.PLAINTEXT
                    },
                    CDK_DEFAULT_REGION: {
                        value: cdk.Aws.REGION,
                        type: codebuild.BuildEnvironmentVariableType.PLAINTEXT
                    },
                    CDK_DEFAULT_ACCOUNT: {
                        value: cdk.Aws.ACCOUNT_ID,
                        type: codebuild.BuildEnvironmentVariableType.PLAINTEXT
                    }
                }
            }
        });
        backendProject.role?.addToPolicy(new iam.PolicyStatement({actions: ["*"], resources: ["*"]}))

        const backendAction = new codepipeline_actions.CodeBuildAction({
            actionName: 'CodeBuild',
            project: backendProject,
            input: sourceArtifact,
            outputs: [backendArtifact] // optional
        });

        // Integration Test backend

        const integrationTestProject = new codebuild.PipelineProject(this, 'backendTestProject',{
            buildSpec: BuildSpec.fromSourceFilename('infra/backendIntegrationBuildspec.yaml'),
            environment: {
                buildImage: codebuild.LinuxBuildImage.STANDARD_5_0,
                environmentVariables: {
                    HOSTING_BUCKET: {
                        value: frontendBucket.bucketName,
                        type: codebuild.BuildEnvironmentVariableType.PLAINTEXT
                    },
                    CDK_DEFAULT_REGION: {
                        value: cdk.Aws.REGION,
                        type: codebuild.BuildEnvironmentVariableType.PLAINTEXT
                    },
                    CDK_DEFAULT_ACCOUNT: {
                        value: cdk.Aws.ACCOUNT_ID,
                        type: codebuild.BuildEnvironmentVariableType.PLAINTEXT
                    }
                }
            }
        });

        const integrationTestArtifact = new codepipeline.Artifact()

        const integrationTestAction = new codepipeline_actions.CodeBuildAction({
            actionName: 'CodeBuild',
            project: integrationTestProject,
            input: backendArtifact,
            outputs: [integrationTestArtifact]
        });

        // pipeline
        const pipeline = new codepipeline.Pipeline(this, 'messagingAppPipeline', {
            pipelineName: "messagingAppPipeline",
            crossAccountKeys: false,
            stages: [
                {
                    stageName: "source",
                    actions: [sourceAction]
                },
                {
                    stageName: 'backend',
                    actions: [backendAction]
                },
                {
                    stageName: 'backendIntegrationTests',
                    actions: [integrationTestAction]
                },
                {
                    stageName: 'frontend',
                    actions: [frontendAction]
                },

            ]

        })


    }
}