import configparser
import datetime
import os
import time

import boto3
from bitbucket_pipes_toolkit import Pipe, enable_debug, get_logger
from retrying import retry

bitbucket_step_oidc_token = os.getenv('BITBUCKET_STEP_OIDC_TOKEN')
aws_oidc_role_arn = os.getenv('AWS_OIDC_ROLE_ARN')
home_path = os.getenv('HOME')


logger = get_logger()
enable_debug()


def setup_oidc_aws_credentials(role_arn, web_identity_token_path, aws_configfile_path):
    config = configparser.ConfigParser()
    config.read(aws_configfile_path)

    config['default'] = {
        'role_arn': role_arn,
        'web_identity_token_file': web_identity_token_path
    }

    with open(aws_configfile_path, 'w') as configfile:
        config.write(configfile)


@retry(wait_random_min=1000, wait_random_max=2000, stop_max_attempt_number=3)
def create_invalidation_request(caller, pipe, distribution_id, paths):
    caller = datetime.datetime.utcnow().isoformat()
    pipe.log_info(
        f"Sending an invalidation request for the distribution id: {distribution_id}")
    pipe.log_info(
        f"Distibution URL: https://console.aws.amazon.com/cloudfront/home?region={region}#distribution-settings:{distribution_id}")

    try:
        invalidation = client.create_invalidation(DistributionId=distribution_id,
                                                  InvalidationBatch={
                                                      'Paths': {
                                                          'Quantity': len(paths),
                                                          'Items': paths
                                                      },
                                                      'CallerReference': caller})

        # print a colorized success message (in green)
        invalidation_id = invalidation['Invalidation']['Id']
        pipe.success(
            f'Successfully created a cloudfront invalidation: {invalidation_id}')

    except Exception as error:
        # log the ERROR message (in red)
        pipe.log_error('Error creating a cloudfront invalidation')

        # print a colorized error message and call system exit
        pipe.fail(f"Failed to create a cloudfront invalidation: {error}")


# defines the schema for pipe variables
variables = {
    'AWS_ACCESS_KEY_ID': {'type': 'string', 'required': True},
    'AWS_SECRET_ACCESS_KEY': {'type': 'string', 'required': True},
    'AWS_DEFAULT_REGION': {'type': 'string', 'required': True},
    'DISTRIBUTION_ID': {'type': 'string', 'required': True},
    'PATHS': {'type': 'string', 'required': False, 'nullable': True, 'default': '/*'},
    'DEBUG': {'type': 'boolean', 'required': False, 'default': False},
}


if aws_oidc_role_arn is not None:
    if bitbucket_step_oidc_token is None:
        logger.warning(
            'Parameter "oidc: true" in the step configuration is required for OIDC authentication')
        logger.info(
            'Using default authentication with AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY.')
    else:
        logger.info(
            'Authenticating with a OpenID Connect (OIDC) Web Identity Provider')

        # default config directory ~/.aws/config
        aws_config_directory = os.path.join(home_path, '.aws')
        oidc_token_directory = os.path.join(aws_config_directory, '.aws-oidc')
        os.makedirs(aws_config_directory, exist_ok=True)
        os.makedirs(oidc_token_directory, exist_ok=True)

        # store token to the file
        random_number = str(time.time_ns())
        oidc_token_path = os.path.join(
            oidc_token_directory, f"oidc_token_{random_number}")
        with open(oidc_token_path, 'w') as f:
            f.write(bitbucket_step_oidc_token)
        os.chmod(oidc_token_path, 0o600)

        # create or update config
        aws_configfile_path = os.path.join(aws_config_directory, 'config')
        setup_oidc_aws_credentials(
            aws_oidc_role_arn, oidc_token_path, aws_configfile_path)

        logger.debug(
            'Configured settings for authentication with assume web identity role')

        # update the schema for pipe variables
        variables['AWS_ACCESS_KEY_ID']['required'] = False
        variables['AWS_SECRET_ACCESS_KEY']['required'] = False

        # unset env variables to prevent aws client general auth
        # https://boto3.amazonaws.com/v1/documentation/api/latest/guide/credentials.html
        if 'AWS_ACCESS_KEY_ID' in os.environ:
            del os.environ['AWS_ACCESS_KEY_ID']
        if 'AWS_SECRET_ACCESS_KEY' in os.environ:
            del os.environ['AWS_SECRET_ACCESS_KEY']
        if 'AWS_SESSION_TOKEN' in os.environ:
            del os.environ['AWS_SESSION_TOKEN']

# initialize the Pipe object. At this stage the validation of variables takes place
pipe = Pipe(schema=variables, check_for_newer_version=True)

region = pipe.get_variable('AWS_DEFAULT_REGION')
distribution_id = pipe.get_variable('DISTRIBUTION_ID')
paths = pipe.get_variable('PATHS').split()

client = boto3.client('cloudfront')

# log the INFO message
pipe.log_info('Sending a cloudfront invalidation request')

# create a unique caller id from BITBUCKET_REPO_FULL_NAME and BITBUCKET_BUILD_NUMBER
# see https://confluence.atlassian.com/bitbucket/variables-in-pipelines-794502608.html
# to get the list of all available environment variables in pipelines
create_invalidation_request(caller, pipe, distribution_id, paths)
