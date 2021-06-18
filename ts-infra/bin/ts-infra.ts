#!/usr/bin/env node
import 'source-map-support/register';
import * as cdk from '@aws-cdk/core';
import { S3Stack } from '../lib/s3-stack';
import {CodeBuildFrontend} from "../lib/frontend-cd-stack";

const app = new cdk.App();


const environment = { account: '423754860743', region: 'eu-west-1' }

new S3Stack(app, 'S3Stack',{env:environment});
new CodeBuildFrontend(app, 'FrontendJob', cdk.Fn.importValue("frontendBucket"), {env:environment})
