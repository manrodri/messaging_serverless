from aws_cdk import core as cdk
from aws_cdk import aws_s3 as s3


class S3Stack(cdk.Stack):

    def __init__(self, scope: cdk.Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # The code that defines your stack goes here
        # frontend bucket
        artifacts_bucket = s3.Bucket(self, 'frontend',
                                     access_control=s3.BucketAccessControl.BUCKET_OWNER_FULL_CONTROL,
                                     encryption=s3.BucketEncryption.S3_MANAGED,
                                     public_read_access=True,
                                     bucket_name='soydecai.xyz',
                                     removal_policy=cdk.RemovalPolicy.DESTROY,
                                     website_index_document='index.html'
                                     )

        cdk.CfnOutput(self, 'frontend-bucket-export',
                      value=artifacts_bucket.bucket_name,
                      export_name='frontend-bucket')
