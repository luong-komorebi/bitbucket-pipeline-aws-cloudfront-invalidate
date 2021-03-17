import os

import boto3

from bitbucket_pipes_toolkit.test import PipeTestCase


STACK_NAME = f"bbci-pipes-test-infrastructure-cloudfront-{os.getenv('BITBUCKET_BUILD_NUMBER')}"
AWS_DEFAULT_REGION = os.getenv("AWS_DEFAULT_REGION")


def get_distribution_id():
    client = boto3.client('cloudformation', region_name=AWS_DEFAULT_REGION)
    resources = client.list_stack_resources(StackName=STACK_NAME)['StackResourceSummaries']

    return [res['PhysicalResourceId'] for res in resources if res['LogicalResourceId'] == 'testDistribution'][0]


class CloudFrontTestCase(PipeTestCase):

    maxDiff = None

    def test_default_success(self):
        result = self.run_container(environment={
            "AWS_ACCESS_KEY_ID": os.getenv("AWS_ACCESS_KEY_ID"),
            "AWS_SECRET_ACCESS_KEY": os.getenv("AWS_SECRET_ACCESS_KEY"),
            "AWS_DEFAULT_REGION": os.getenv("AWS_DEFAULT_REGION"),
            "DISTRIBUTION_ID": get_distribution_id(),
        })

        self.assertIn('Successfully created a cloudfront invalidation', result)

    def test_with_multiple_paths(self):
        result = self.run_container(environment={
            "AWS_ACCESS_KEY_ID": os.getenv("AWS_ACCESS_KEY_ID"),
            "AWS_SECRET_ACCESS_KEY": os.getenv("AWS_SECRET_ACCESS_KEY"),
            "AWS_DEFAULT_REGION": os.getenv("AWS_DEFAULT_REGION"),
            "DISTRIBUTION_ID": get_distribution_id(),
            "PATHS": "/index.html /home.html"
        })

        self.assertIn('Successfully created a cloudfront invalidation', result)

    def test_invalidation_is_created_in_aws(self):
        distribution_id = get_distribution_id()
        result = self.run_container(environment={
            "AWS_ACCESS_KEY_ID": os.getenv("AWS_ACCESS_KEY_ID"),
            "AWS_SECRET_ACCESS_KEY": os.getenv("AWS_SECRET_ACCESS_KEY"),
            "AWS_DEFAULT_REGION": os.getenv("AWS_DEFAULT_REGION"),
            "DISTRIBUTION_ID": distribution_id,
            "PATHS": "/index.html /home.html"
        })

        client = boto3.client('cloudfront', region_name=os.getenv("AWS_DEFAULT_REGION"))
        invalidations = client.list_invalidations(DistributionId=distribution_id)

        invalidation_id = invalidations['InvalidationList']['Items'][0]['Id']
        text = f"Successfully created a cloudfront invalidation: {invalidation_id}"
        self.assertIn(text, result)

    def test_distribution_doesnt_exist(self):
        result = self.run_container(environment={
            "AWS_ACCESS_KEY_ID": os.getenv("AWS_ACCESS_KEY_ID"),
            "AWS_SECRET_ACCESS_KEY": os.getenv("AWS_SECRET_ACCESS_KEY"),
            "AWS_DEFAULT_REGION": os.getenv("AWS_DEFAULT_REGION"),
            "DISTRIBUTION_ID": 'invalidId',
        })

        self.assertIn('The specified distribution does not exist', result)

    def test_fail_if_no_required_variables(self):
        result = self.run_container(environment={
            "DISTRIBUTION_ID": get_distribution_id(),
        })

        self.assertRegex(result, rf'✖ Validation errors')


class CloudFrontOIDCTestCase(PipeTestCase):
    maxDiff = None

    def test_default_success(self):
        result = self.run_container(environment={
            "AWS_DEFAULT_REGION": os.getenv("AWS_DEFAULT_REGION"),
            "DISTRIBUTION_ID": get_distribution_id(),
            "AWS_OIDC_ROLE_ARN": os.getenv("AWS_OIDC_ROLE_ARN"),
            "BITBUCKET_STEP_OIDC_TOKEN": os.getenv("BITBUCKET_STEP_OIDC_TOKEN"),
        })

        self.assertIn('Authenticating with a OpenID Connect (OIDC) Web Identity Provider', result)
        self.assertIn('Successfully created a cloudfront invalidation', result)

    def test_success_all_auth_method_provided(self):
        result = self.run_container(environment={
            "AWS_ACCESS_KEY_ID": os.getenv("AWS_ACCESS_KEY_ID"),
            "AWS_SECRET_ACCESS_KEY": os.getenv("AWS_SECRET_ACCESS_KEY"),
            "AWS_DEFAULT_REGION": os.getenv("AWS_DEFAULT_REGION"),
            "DISTRIBUTION_ID": get_distribution_id(),
            "AWS_OIDC_ROLE_ARN": os.getenv("AWS_OIDC_ROLE_ARN"),
            "BITBUCKET_STEP_OIDC_TOKEN": os.getenv("BITBUCKET_STEP_OIDC_TOKEN"),
        })

        self.assertIn('Authenticating with a OpenID Connect (OIDC) Web Identity Provider', result)
        self.assertIn('Successfully created a cloudfront invalidation', result)

    def test_success_swith_to_general_auth_if_no_oidc_token(self):
        result = self.run_container(environment={
            "AWS_ACCESS_KEY_ID": os.getenv("AWS_ACCESS_KEY_ID"),
            "AWS_SECRET_ACCESS_KEY": os.getenv("AWS_SECRET_ACCESS_KEY"),
            "AWS_DEFAULT_REGION": os.getenv("AWS_DEFAULT_REGION"),
            "DISTRIBUTION_ID": get_distribution_id(),
            "AWS_OIDC_ROLE_ARN": os.getenv("AWS_OIDC_ROLE_ARN"),
        })

        self.assertIn('Parameter "oidc: true" in the step configuration is required for OIDC authentication', result)
        self.assertIn('Using default authentication with AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY', result)
        self.assertIn('Successfully created a cloudfront invalidation', result)
