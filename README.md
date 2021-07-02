# Bitbucket Pipelines Pipe: AWS CloudFront create invalidation

Create an invalidation of your CloudFront distribution

Remove a file(s) from CloudFront edge caches before it expires. The next time a viewer requests the file, CloudFront returns to the origin to fetch the latest version of the file. This is specially useful to refresh the content served by static websites deployed to S3 buckets. For more information about file invalidation in CloudFront, please, check the AWS official docs (https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/Invalidation.html).
You can use Amazon CloudFront to improve the performance of your website. CloudFront makes your website’s files (such as HTML, images, and video) available from data centers around the world (called edge locations). When a visitor requests a file from your website, CloudFront automatically redirects the request to a copy of the file at the nearest edge location. This results in faster download times than if the visitor had requested the content from a data center that is located farther away.

## YAML Definition

Add the following snippet to the script section of your `bitbucket-pipelines.yml` file:

```yaml
- pipe: atlassian/aws-cloudfront-invalidate:0.6.0
  variables:
    AWS_ACCESS_KEY_ID: '<string>' # Optional if already defined in the context or OIDC used.
    AWS_SECRET_ACCESS_KEY: '<string>' # Optional if already defined in the context or OIDC used.
    AWS_DEFAULT_REGION: '<string>' # Optional if already defined in the context.
    AWS_OIDC_ROLE_ARN: "<string>" # Optional by default. Required for OpenID Connect (OIDC) authentication.
    DISTRIBUTION_ID: "<string>"
    # PATHS: "<string>" # Optional
    # DEBUG: "<boolean>" # Optional
```

## Variables

| Variable              | Usage                                                       |
| --------------------- | ----------------------------------------------------------- |
| AWS_ACCESS_KEY_ID (**) | AWS access key id |
| AWS_SECRET_ACCESS_KEY (**) | AWS secret key |
| AWS_DEFAULT_REGION (**) | AWS region |
| AWS_OIDC_ROLE_ARN     | The ARN of the role used for web identity federation or OIDC. See **Authentication**. |
| DISTRIBUTION_ID (*)   | The id of your CloudFront distribution. |
| PATHS                 | List of white space separated paths to invalidate. Default: `/*`.|
| DEBUG                 | Turn on extra debug information. Default: `false`. |
_(*) = required variable. This variable needs to be specified always when using the pipe._
_(**) = required variable. If this variable is configured as a repository, account or environment variable, it doesn’t need to be declared in the pipe as it will be taken from the context. It can still be overridden when using the pipe._



## Prerequisites

1. CloudFront distribution set up. Here are the details about how to create a CloudFront distribution, with an AWS S3 origin: https://docs.aws.amazon.com/AmazonS3/latest/dev/website-hosting-cloudfront-walkthrough.html
2. CloudFront distribution id. It can obtained from the CloudFront AWS console: https://console.aws.amazon.com/cloudfront/


## Authentication

Supported options:

1. Environment variables: AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY. Default option.

2. Assume role provider with OpenID Connect (OIDC). More details in the Bitbucket Pipelines Using OpenID Connect guide [Integrating aws bitbucket pipeline with oidc][aws-oidc]. Make sure that you setup OIDC before:
    * configure Bitbucket Pipelines as a Web Identity Provider in AWS
    * attach to provider your AWS role with required policies in AWS
    * setup a build step with `oidc: true` in your Bitbucket Pipelines
    * pass AWS_OIDC_ROLE_ARN (*) variable that represents role having appropriate permissions to execute actions on Cloudfront resources



## Examples

### Basic example:

Creating and invalidation:

```yaml
script:
  - pipe: atlassian/aws-cloudfront-invalidate:0.6.0
    variables:
      AWS_ACCESS_KEY_ID: $AWS_ACCESS_KEY_ID
      AWS_SECRET_ACCESS_KEY: $AWS_SECRET_ACCESS_KEY
      AWS_DEFAULT_REGION: $AWS_DEFAULT_REGION
      DISTRIBUTION_ID: '123xyz'
```

Example creating and invalidation. `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY` and `AWS_DEFAULT_REGION` are configured as repository variables, so there is no need to declare them in the pipe.

```yaml
script:
  - pipe: atlassian/aws-cloudfront-invalidate:0.6.0
    variables:
      DISTRIBUTION_ID: '123xyz'
```

### Advanced example:

Deploy a new version of your CloudFormation stack with OpenID Connect (OIDC) alternative authentication without required `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`.
Parameter `oidc: true` in the step configuration and variable `AWS_OIDC_ROLE_ARN` are required:

```yaml
- step:
    oidc: true
    script:
      - pipe: atlassian/aws-cloudfront-invalidate:0.6.0
        variables:
          AWS_DEFAULT_REGION: $AWS_DEFAULT_REGION
          AWS_OIDC_ROLE_ARN: 'arn:aws:iam::123456789012:role/role_name'
          DISTRIBUTION_ID: '123xyz'
```

Creating an invalidation for a list of paths:

```yaml
script:
  - pipe: atlassian/aws-cloudfront-invalidate:0.6.0
    variables:
      AWS_ACCESS_KEY_ID: $AWS_ACCESS_KEY_ID
      AWS_SECRET_ACCESS_KEY: $AWS_SECRET_ACCESS_KEY
      AWS_DEFAULT_REGION: $AWS_DEFAULT_REGION
      DISTRIBUTION_ID: '123xyz'
      PATHS: '/index.html /home.html'
```

Example using an `aws-s3-deploy` pipe to sync your files to S3 and triggering a distribution invalidation to refresh the CDN caches:
```
script:
  - pipe: atlassian/aws-s3-deploy:0.3.2
    variables:
      AWS_ACCESS_KEY_ID: $AWS_ACCESS_KEY_ID
      AWS_SECRET_ACCESS_KEY: $AWS_SECRET_ACCESS_KEY
      AWS_DEFAULT_REGION: 'us-east-1'
      S3_BUCKET: 'my-bucket-name'
      LOCAL_PATH: 'build'

  - pipe: atlassian/aws-cloudfront-invalidate:0.6.0
    variables:
      AWS_ACCESS_KEY_ID: $AWS_ACCESS_KEY_ID
      AWS_SECRET_ACCESS_KEY: $AWS_SECRET_ACCESS_KEY
      AWS_DEFAULT_REGION: $AWS_DEFAULT_REGION
      DISTRIBUTION_ID: '123xyz'
```


## Support
If you’d like help with this pipe, or you have an issue or feature request, [let us know on Community][community].

If you’re reporting an issue, please include:

- the version of the pipe
- relevant logs and error messages
- steps to reproduce


## License
Copyright (c) 2019 Atlassian and others.
Apache 2.0 licensed, see [LICENSE.txt](LICENSE.txt) file.


[community]: https://community.atlassian.com/t5/forums/postpage/board-id/bitbucket-pipelines-questions?add-tags=pipes,aws,cloudfront
[aws-oidc]: https://support.atlassian.com/bitbucket-cloud/docs/deploy-on-aws-using-bitbucket-pipelines-openid-connect
