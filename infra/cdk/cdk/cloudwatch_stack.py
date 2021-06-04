from aws_cdk import (
    core,
    aws_cloudfront as cloudfront,
    aws_cloudwatch as cloudwatch
)


class CloudWatchStack(core.Stack):
    # def __init__(
    #         self,
    #         scope: core.Construct, id: str,
    #         cdn: cloudfront.Distribution,
    #         **kwargs) -> None:
    #     super().__init__(scope, id, **kwargs)
    #
    #     metric = cloudwatch.Metric(
    #         namespace="AWS/Route53",
    #         metric_name="DNSQueries",
    #         dimensions={
    #             "HostedZoneId": hosted_zone.hosted_zone_id
    #         }
    #     )
    pass

