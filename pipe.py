import datetime

import boto3

from bitbucket_pipes_toolkit import Pipe

# defines the schema for pipe variables
variables = {
    'AWS_ACCESS_KEY_ID': {'type': 'string', 'required': True},
    'AWS_SECRET_ACCESS_KEY': {'type': 'string', 'required': True},
    'AWS_DEFAULT_REGION': {'type': 'string', 'required': True},
    'DISTRIBUTION_ID': {'type': 'string', 'required': True},
    'PATHS': {'type': 'string', 'required': False, 'nullable': True, 'default': '/*'},
    'DEBUG': {'type': 'boolean', 'required': False, 'default': False}

}

# initialize the Pipe object. At this stage the validation of variables takes place
pipe = Pipe(schema=variables)

region = pipe.get_variable('AWS_DEFAULT_REGION')
distribution_id = pipe.get_variable('DISTRIBUTION_ID')
paths = pipe.get_variable('PATHS').split()

client = boto3.client('cloudfront')

# log the INFO message
pipe.log_info('Senging a cloudfront invalidation request')

# create a unique caller id from BITBUCKET_REPO_FULL_NAME and BITBUCKET_BUILD_NUMBER
# see https://confluence.atlassian.com/bitbucket/variables-in-pipelines-794502608.html
# to get the list of all available environment variables in pipelines

caller = datetime.datetime.utcnow().isoformat()

pipe.log_info(f"Sending an invalidation request for the distribution id: {distribution_id}")
pipe.log_info(f"Distibution URL: https://console.aws.amazon.com/cloudfront/home?region={region}#distribution-settings:{distribution_id}")

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
    pipe.success(f'Successfully created a cloudfront invalidation: {invalidation_id}')

except Exception as error:
    # log the ERROR message (in red)
    pipe.log_error('Error creating a cloudfront invalidation')

    # print a colorized error message and call system exit
    pipe.fail(f"Failed to create a cloudfront invalidation: {error}")
