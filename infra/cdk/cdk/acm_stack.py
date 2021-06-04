from aws_cdk import (
    aws_certificatemanager as acm,
    aws_route53 as r53,
    aws_iam as iam,
    aws_cloudfront as cdn,
    aws_ssm as ssm,
    core
)


class ACMStack(core.Stack):

    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        prj_name = self.node.try_get_context("project_name")
        env_name = self.node.try_get_context("env")
        domain_name = self.node.try_get_context('domain_name')

        hosted_zone = r53.HostedZone.from_lookup(self, 'hosted-zone',
                                                 domain_name=domain_name
                                                 )
        # dns_zone = r53.HostedZone.from_hosted_zone_attributes(self, 'hosted-zone',
        #                                                       hosted_zone_id=hosted_zone.hosted_zone_id,
        #                                                       zone_name='soydecai.xyz'
        #                                                       )

        self.cert_manager = acm.DnsValidatedCertificate(self, 'acm-id',
                                                        hosted_zone=hosted_zone,
                                                        domain_name=domain_name,
                                                        subject_alternative_names=[f'*.{domain_name}']
                                                        )

        ssm.StringParameter(self,
                            'certificate-arn',
                            parameter_name=f"/{env_name}/acm-certificate-arn",
                            string_value=self.cert_manager.certificate_arn)
