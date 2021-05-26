from aws_cdk import (
    aws_route53 as r53,
    aws_route53_targets as r53target,
    aws_iam as iam,
    aws_s3 as s3,
    aws_ssm as ssm,
    core
)


class DnsStack(core.Stack):

    def __init__(self, scope: core.Construct, id: str, frontendBucket, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        prj_name = self.node.try_get_context("project_name")
        env_name = self.node.try_get_context("env")
        domain_name = self.node.try_get_context("domain_name")

        webhostingbucket = s3.Bucket.from_bucket_name(self, 'webhosting-bucket',
                                                      bucket_name=frontendBucket)

        hosted_zone = r53.HostedZone.from_lookup(self, 'hosted-zone',
                                     domain_name=domain_name
                                     )

        r53.ARecord(self, 'cdn-record',
                    zone=hosted_zone,
                    target=r53.RecordTarget.from_alias(alias_target=r53target.BucketWebsiteTarget(webhostingbucket)),
                    record_name=domain_name
                    )

        ssm.StringParameter(self, 'zone-id',
                            parameter_name='/' + env_name + '/zone-id',
                            string_value=hosted_zone.hosted_zone_id
                            )
