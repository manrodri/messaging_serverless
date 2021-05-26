#!/usr/bin/env python3
import os
from aws_cdk import core

from cdk.s3_stack import S3Stack
from cdk.DNS_stack import DnsStack


app = core.App()
s3_stack = S3Stack(app, "CdkStack")
dns_stack = DnsStack(app,
                     'DNSStack',
                     frontendBucket=core.Fn.import_value('frontend-bucket'),
                     env=core.Environment(
                        account=os.environ["CDK_DEFAULT_ACCOUNT"],
                        region=os.environ["CDK_DEFAULT_REGION"])
                     )
app.synth()
