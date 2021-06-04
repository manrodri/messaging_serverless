from aws_cdk import (
    aws_s3 as s3,
    aws_cloudfront as cdn,
    aws_ssm as ssm,
    aws_certificatemanager as cm,
    core
)


class CDNStack(core.Stack):

    def __init__(self, scope: core.Construct, id: str, s3bucket, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        prj_name = self.node.try_get_context("project_name")
        env_name = self.node.try_get_context("env")

        bucketName = s3.Bucket.from_bucket_name(self, 's3bucket', s3bucket)
        certificate_arn = \
            cm.Certificate.from_certificate_arn(
                self,
                'certifiacate',
                certificate_arn=
                'arn:aws:acm:us-east-1:423754860743:certificate/e8565981-f777-43bd-af7f-977a92de4f93').certificate_arn


        self.cdn_id = cdn.CloudFrontWebDistribution(self, 'webhosting-cdn',
                                                    origin_configs=[cdn.SourceConfiguration(
                                                        behaviors=[
                                                            cdn.Behavior(is_default_behavior=True)
                                                        ],
                                                        s3_origin_source=cdn.S3OriginConfig(
                                                            s3_bucket_source=bucketName,
                                                            origin_access_identity=cdn.OriginAccessIdentity(self,
                                                                                                            'webhosting-origin')
                                                        )

                                                    )],
                                                    error_configurations=[
                                                        cdn.CfnDistribution.CustomErrorResponseProperty(
                                                            error_code=400,
                                                            response_code=200,
                                                            response_page_path="/"

                                                        ),
                                                        cdn.CfnDistribution.CustomErrorResponseProperty(
                                                            error_code=403,
                                                            response_code=200,
                                                            response_page_path="/"
                                                        ),
                                                        cdn.CfnDistribution.CustomErrorResponseProperty(
                                                            error_code=404,
                                                            response_code=200,
                                                            response_page_path="/"
                                                        )
                                                    ],
                                                    alias_configuration=cdn.AliasConfiguration(
                                                        acm_cert_ref=certificate_arn,
                                                        names=['app.soydecai.xyz']
                                                    )

                                                    )

        ssm.StringParameter(self, 'cdn-dist-id',
                            parameter_name='/' + env_name + '/app-distribution-id',
                            string_value=self.cdn_id.distribution_id
                            )

        ssm.StringParameter(self, 'cdn-url',
                            parameter_name='/' + env_name + '/app-cdn-url',
                            string_value='https://' + self.cdn_id.domain_name
                            )

