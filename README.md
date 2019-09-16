# Bitbucket Pipelines Pipe: AWS CloudFront create invalidation

Create an invalidation of your CloudFront distribution

## YAML Definition

Add the following snippet to the script section of your `bitbucket-pipelines.yml` file:

```yaml
- pipe: atlassian/aws-cloudfront-invalidate:0.0.0
  variables:
    AWS_ACCESS_KEY_ID: "<string>"
    AWS_SECRET_ACCESS_KEY: "<string>"
    AWS_DEFAULT_REGION: "<string>"
    DISTRIBUTION_ID: "<string>"
    # PATHS: "<string>" # Optional
    # DEBUG: "<boolean>" # Optional
```
## Variables

| Variable              | Usage                                                       |
| --------------------- | ----------------------------------------------------------- |
| AWS_ACCESS_KEY_ID (*) | AWS access key id |
| AWS_SECRET_ACCESS_KEY (*) | AWS secret key |
| AWS_DEFAULT_REGION (*) | AWS region |
| DISTRIBUTION_ID (*)   | The id of your CloudFront distribution. |
| PATHS                   | List of white space separated paths to invalidate. Default: `/*`.|
| DEBUG                 | Turn on extra debug information. Default: `false`. |

_(*) = required variable._

## Prerequisites


## Examples

Basic example creating and invalidation:

```yaml
script:
  - pipe: atlassian/aws-cloudfront-invalidate:0.0.0
    variables:
      AWS_ACCESS_KEY_ID: $AWS_ACCESS_KEY_ID
      AWS_SECRET_ACCESS_KEY: $AWS_SECRET_ACCESS_KEY
      AWS_DEFAULT_REGION: $AWS_DEFAULT_REGION
      DISTRIBUTION_ID: '123xyz'
```

Advanced example creating an invalidation for a list of paths:

```yaml
script:
  - pipe: atlassian/aws-cloudfront-invalidate:0.0.0
    variables:
      AWS_ACCESS_KEY_ID: $AWS_ACCESS_KEY_ID
      AWS_SECRET_ACCESS_KEY: $AWS_SECRET_ACCESS_KEY
      AWS_DEFAULT_REGION: $AWS_DEFAULT_REGION
      DISTRIBUTION_ID: '123xyz'
      PATHS: '/index.html /home.html'
```

## Support
If you’d like help with this pipe, or you have an issue or feature request, [let us know on Community](https://community.atlassian.com/t5/forums/postpage/choose-node/true/interaction-style/qanda?add-tags=bitbucket-pipelines,pipes).

If you’re reporting an issue, please include:

- the version of the pipe
- relevant logs and error messages
- steps to reproduce
