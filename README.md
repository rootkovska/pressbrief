# Pressbrief

A user-controlled automation for generating daily press briefs.

## What

This project is a user-controlled automation (packaged to conveniently run in a docker container) for generating daily press briefs. This machinery expects only one essential input file:

- `config.yaml` containing newspapers described by name and RSS feeds that should be included in a brief.

- and at least one of the following options for storing data:
    - `HOST_OUTPUT` and `BRIEF_OUTPUT` to save it locally,
    - `DROPBOX_ACCESS_TOKEN` to upload it to Dropbox.

Once given the above parameters, the following algorithm is used to assemble a daily brief:

1. The set of provided newspapers in the `config.yaml` file is read.

2. For each of these provided newspapers, the list of news are read from that newspaper's RSS feeds.

3. All these news from all the provided newspapers are combined into one single list. This combined list is then trimmed so it fits on a few pages when news are printed (yes, that means lots of trimming!).

4. A 2-column page PDF is generated, presenting all the news obtained in the previous step. This PDF is made available through an `HOST_OUTPUT` volume for further consumption by the user.

### Configuration

The whole configuration is defined via a `.env` file containing required parameters that are used then to deploy the application locally as a Docker container or to a cloud infrastructure as an AWS Lambda function.

```sh
# AWS credentials
AWS_ACCESS_KEY_ID=...
AWS_SECRET_ACCESS_KEY=...
AWS_DEFAULT_REGION=...

# Pressbrief parameters
DROPBOX_ACCESS_TOKEN=...
HOST_OUTPUT=./output
BRIEF_OUTPUT=/output
LIMIT_PER_RSS=32
URL2QR=False
```

As seen above, it is also possible to configure the some secondary params, which otherwise should get sane defaults:

- `LIMIT_PER_RSS` -- the maximum number of news from one RSS feed to include (step `#2`). Default `4`.

- `URL2QR` --  the flag indicating whether URLs should be converted to QR codes. Default `True`.

For a cloud deployment, the following parameters are required:

- `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY` assigned to an IAM with the permissions listed below:
    - `AWSCloudFormationFullAccess`
    - `AWSLambdaFullAccess`
    - `IAMFullAccess`
    - optional: to restrict the above permissions, create a custom policy with actions included in `aws-policy.json` file (reference: [IAM JSON Policy Reference](https://docs.aws.amazon.com/IAM/latest/UserGuide/reference_policies.html))

- `AWS_DEFAULT_REGION` -- the AWS region in which resources will be created.

### Deployment

The deployment process are performed using one of the available scripts:

- `./docker-compose.aws.yaml` for AWS deployment via `docker-compose`,

- `./docker-compose.yaml` for local deployments via `docker-compose`.

Both of them require Docker and Docker Compose installed.

## How

### RSS

The connection to RSS feeds is made using the Python package [feedparser](https://github.com/kurtmckee/feedparser). The library was chosen because of its stability and regular patches.

### PDF

The PDF files are generated using the Python package [weasyprint](https://github.com/Kozea/WeasyPrint), which allow to convert an HTML page to a PDF page. From many available solutions this one was chosen beacuse of CSS flexbox and columns support which made it easy to generate 2-columns page PDF files.

### Dropbox

Uploading files to Dropbox is implemented using the Python package [dropbox](https://github.com/dropbox/dropbox-sdk-python) which is the official Dropbox API Client for integrating with the Dropbox API v2. Its use requires the creation of a Dropbox App which will allow to get an access token. The detailed instruction is available at this [link](https://www.dropbox.com/developers/reference/getting-started#app%20console).

### AWS

An automated deployment to AWS is performed using a CloudFormation template which describe all resources, roles and permissions needed to execute the application. In addition, a GitHub Workflow is configured so the deployment is triggered on every push to the master branch.

## Debug

The following commands might be helpful in debugging:

* to get info about the function:
```sh
docker run \
    --interactive \
    --env-file .env \
    pressbrief-aws \
        aws lambda get-function \
            --function-name Pressbrief
```

* to trigger the function:
```sh
docker run \
    --interactive \
    --env-file .env \
    pressbrief-aws \
        aws lambda invoke \
            --function-name Pressbrief \
            --invocation-type Event \
            /dev/null
```