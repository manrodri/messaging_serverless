import * as cdk from "@aws-cdk/core";
import * as codepipeline from '@aws-cdk/aws-codepipeline';
import {GitHubSourceAction, CodeBuildAction} from '@aws-cdk/aws-codepipeline-actions';
import * as codebuild from "@aws-cdk/aws-codebuild";
import * as pipeline from "@aws-cdk/pipelines"

export class backendCpStack extends cdk.Stack {
    constructor(scope: cdk.Construct, id: string, props?: cdk.StackProps) {
        super(scope, id, props);

        const pipeline = new codepipeline.Pipeline(this, 'BackendPipeline',
            {
                pipelineName: 'BackendPipeline',
                crossAccountKeys: false,
            });

        // source action
        const gitHubToken = cdk.SecretValue.secretsManager('remoteRepositorieKeys', {
            jsonField: 'GitHub_key'
        })

        const sourceOutput = new codepipeline.Artifact();
        const sourceAction = new GitHubSourceAction({
            actionName: 'GitHub_Source',
            owner: 'manrodri',
            repo: 'messaging_serverless',
            oauthToken: gitHubToken,
            output: sourceOutput,
            branch: 'ts', // default: 'master'
        });
        pipeline.addStage({
            stageName: 'Source',
            actions: [sourceAction],
        });

        const cloudAssemblyArtifact = new codepipeline.Artifact()

        // build action
        const project = new codebuild.PipelineProject(this, 'BuildBackendProject');

        const buildAction = new CodeBuildAction({
            actionName: 'CodeBuild',
            project,
            input: sourceOutput,
            outputs: [cloudAssemblyArtifact], // optional
        });

        pipeline.addStage({
            stageName: 'Build',
            actions: [buildAction]
        })


    }
}