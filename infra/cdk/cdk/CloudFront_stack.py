import aws_cdk.core as core
import aws_cdk.aws_cloudfront as cloudfront
import aws_cdk.aws_cloudfront_origins as origins
import aws_cdk.aws_s3 as s3

class CdnStack(core.Stack):

    def __init__(
            self,
            scope: core.Construct, id: str,
            frontendBucket,
            **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        webhostingbucket = s3.Bucket.from_bucket_name(self, 'webhosting-bucket',
                                                      bucket_name=frontendBucket)

        cloudfront.Distribution(self, "myDist",
                                default_root_object='index.html',
                                default_behavior=cloudfront.BehaviorOptions(origin=origins.S3Origin(webhostingbucket))
                                )




