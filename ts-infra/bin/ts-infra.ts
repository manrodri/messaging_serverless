#!/usr/bin/env node
import 'source-map-support/register';
import * as cdk from '@aws-cdk/core';
import { S3Stack } from '../lib/s3-stack';
import {LambdaStack} from "../lib/lambda-stack";
import {messagingAppPipelineStack} from "../lib/cdkpipeline-definition-stack";

const app = new cdk.App();

const region = process.env.CDK_DEFAULT_REGION || 'eu-west-1'
const account = process.env.CDK_DEFAULT_ACCOUNT || '423754860743'
const environment = { account: account, region: region }

new S3Stack(app, 'S3Stack',{env:environment});
const backendStack = new LambdaStack(app, 'backendStack',cdk.Fn.importValue("frontendBucket"), {env: environment})
new messagingAppPipelineStack(app, 'pipelineStack', cdk.Fn.importValue("frontendBucket"), {
    env: environment
})


app.synth()