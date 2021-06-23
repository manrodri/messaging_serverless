import * as codepipeline from '@aws-cdk/aws-codepipeline';
import * as codepipeline_actions from '@aws-cdk/aws-codepipeline-actions';
import {Construct, SecretValue, Stack, StackProps} from '@aws-cdk/core';
import {CdkPipeline, SimpleSynthAction} from "@aws-cdk/pipelines";
import * as cdk from "@aws-cdk/core";

/**
 * The stack that defines the application pipeline
 */
export class CdkpipelinesDemoPipelineStack extends Stack {
    constructor(scope: Construct, id: string, props?: StackProps) {
        super(scope, id, props);

        // artifacts buckets
        const sourceArtifact = new codepipeline.Artifact();
        const cloudAssemblyArtifact = new codepipeline.Artifact();

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

        // pipeline
        const pipeline = new CdkPipeline(this, 'Pipeline', {
            pipelineName: 'MyServicePipeline',
            cloudAssemblyArtifact,
            sourceAction: sourceAction,

            // How it will be built and synthesized
            synthAction: SimpleSynthAction.standardNpmSynth({
                sourceArtifact,
                cloudAssemblyArtifact,

                // We need a build step to compile the TypeScript Lambda
                // buildCommand: 'npm run build'
                synthCommand: "cdk synth"
            }),
        });

        // This is where we add the application stages
        // ...
    }
}