#!/usr/bin/env node
import * as cdk from '@aws-cdk/core';
import {BackendStack} from '../lib/backend-stack';
import {S3Stack} from "../lib/s3-stack";
import {messagingAppPipelineStack} from "../lib/cdkpipeline-definition-stack";

const region = process.env.CDK_DEFAULT_REGION || 'eu-west-1'
const account = process.env.CDK_DEFAULT_ACCOUNT || '423754860743'
const environment = {account: account, region: region}

const app = new cdk.App();

const s3Stack = new S3Stack(app, 'S3Stack')
new BackendStack(app,
    'BackendStack',
    cdk.Fn.importValue("frontendBucket"),
    {env: environment});
new messagingAppPipelineStack(app,
    'PipelineStack',
    cdk.Fn.importValue('frontendBucket'),
    {env: environment})


app.synth()