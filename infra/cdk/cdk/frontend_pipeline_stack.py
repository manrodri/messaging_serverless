from aws_cdk import (
    aws_codepipeline as cp,
    aws_codepipeline_actions as cp_actions,
    aws_codecommit as ccm,
    aws_codebuild as cb,
    aws_s3 as s3,
    aws_iam as iam,
    aws_ssm as ssm,
    core
)


class CodePipelineFrontendStack(core.Stack):

    def __init__(self, scope: core.Construct, id: str, webhostingbucket, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        prj_name = self.node.try_get_context("project_name")
        env_name = self.node.try_get_context("env")

        webhosting_bucket = s3.Bucket.from_bucket_name(self, 'webhosting-id', bucket_name=webhostingbucket)

        cdn_id = ssm.StringParameter.from_string_parameter_name(self, 'cdnid',
                                                                string_parameter_name='/' + env_name + '/app-distribution-id')
        source_repo = ccm.Repository.from_repository_name(self,
                                                          'repoid',
                                                          repository_name='messaging_serverless',
                                                          )

        artifact_bucket = s3.Bucket(self, 'artifactbucketid',
                                    encryption=s3.BucketEncryption.S3_MANAGED,
                                    access_control=s3.BucketAccessControl.BUCKET_OWNER_FULL_CONTROL
                                    )

        build_project = cb.PipelineProject(self, 'buildfrontend',
                                           project_name='BuildFrontend',
                                           description='frontend project for SPA',
                                           environment=cb.BuildEnvironment(
                                               build_image=cb.LinuxBuildImage.STANDARD_5_0,
                                               environment_variables={
                                                   'HOSTING_BUCKET': cb.BuildEnvironmentVariable(
                                                       value=webhosting_bucket.bucket_name
                                                   ),
                                                   'DISTRIBUTION_ID': cb.BuildEnvironmentVariable(
                                                       value=cdn_id.string_value
                                                   )
                                               }
                                           ),
                                           cache=cb.Cache.bucket(bucket=artifact_bucket, prefix='codebuild-cache'),
                                           build_spec=cb.BuildSpec.from_object({
                                               'version': '0.2',
                                               'phases': {
                                                   'install': {
                                                       'commands': [
                                                           'pip install awscli'
                                                       ]
                                                   },
                                                   'build': {
                                                       'commands': [
                                                           'aws s3 sync ./lib/Site/ s3://${HOSTING_BUCKET}'
                                                       ]
                                                   },
                                                   'post_build': {
                                                       'commands': [
                                                           'aws cloudfront create-invalidation --distribution-id ${DISTRIBUTION_ID} --paths "/*" '
                                                       ]
                                                   }
                                               }
                                           })
                                           )

        pipeline = cp.Pipeline(self, 'frontend-pipeline',
                               pipeline_name=prj_name + '-' + env_name + '-frontend-pipeline',
                               artifact_bucket=artifact_bucket,
                               restart_execution_on_update=False
                               )

        source_output = cp.Artifact(artifact_name='source')
        build_output = cp.Artifact(artifact_name='build')

        pipeline.add_stage(stage_name='Source', actions=[
            cp_actions.CodeCommitSourceAction(
                action_name='CodeCommitSource',
                repository=source_repo,
                output=source_output,
                branch='dev'
            )
        ])

        pipeline.add_stage(stage_name='Build', actions=[
            cp_actions.CodeBuildAction(
                action_name='Build',
                input=source_output,
                project=build_project,
                outputs=[build_output]
            )
        ])
        # TODO: restrict IAM policy
        build_project.role.add_to_policy(iam.PolicyStatement(
            actions=['*'],
            resources=['*']
        ))