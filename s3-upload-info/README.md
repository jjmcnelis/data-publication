# data-publication/s3-upload-info
This directory contains resources for data providers to assist with data delivery to PODAAC-managed s3 buckets.

* [Getting Started](#getting-started)
* [Automate Credential Rotation](#automate-credential-rotation)

## Getting Started

Table of Contents:
1. AWS Credentials
	a. How to get AWS credentials
	b. Set up AWS credentials with environment variables
	c. Set up AWS credentials with credential files and profiles
		a. How to activate an AWS profile with environment variables
		b. How to activate an AWS profile in the AWS CLI
	d. Confirm credentials are working
1. Copy data to PO.DAAC using the AWS CLI
2. Copy data to PO.DAAC using Python


### AWS Credentials

#### How to retrieve AWS Credentials

AWS Credentials will be provided in a CSV with the following format:

| User name              | Password | Access key ID        | Secret access key                        | Console login link |
| ---------------------- | -------- | -------------------- | ---------------------------------------- | ------------------ |
| SRV-podaac-dev-mission |          | ABCD1234567890123456 | abcdefghijklmnopqrstuvwxyz1234567890abcd | ...                |

Updated AWS credentials will be sent via JPL LFT every few months as the old credentials expire.

#### Set up AWS credentials with environment variables

You can set environment variables to temporarily configure your shell with AWS access. 

```bash
export AWS_ACCESS_KEY_ID=ABCD1234567890123456
export AWS_SECRET_ACCESS_KEY=abcdefghijklmnopqrstuvwxyz1234567890abcd
```

For more information on AWS environment variables, [see the AWS docs.](https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-envvars.html)

#### Set up AWS credentials with credential files and profiles (recommended)

To set up your AWS credentials permanently, you can set up an AWS credentials file. This can be set up manually or using the AWS CLI. To set up your credentials using the AWS CLI, run the following command:

```bash
aws configure
```

This will prompt you to enter your AWS credentials values. Alternatively, you can manually set up your AWS credentials file like so:

In file `~/.aws/credentials`:

```bash
[myprofilename]
aws_access_key_id = ABCD1234567890123456
aws_secret_access_key = abcdefghijklmnopqrstuvwxyz1234567890abcd
region = us-west-2
```

Replace `myprofilename` with the name of your choice. If you choose `default`, the profile will be activated by default without the need to manually activate or specify the profile. 

For more details on AWS credentials files, [see the AWS docs.](https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-files.html). 

#### How to activate an AWS profile

There are two ways to activate or specify an AWS profile. 

##### Activate AWS Profile using environment variables

You can activate a profile called `myprofilename` by setting the `AWS_PROFILE` environment variable like so:

```bash
export AWS_PROFILE=myprofilename
```

##### Activate AWS Profile using the AWS CLI

You can set the profile in each AWS CLI command if desired. For instance, the following AWS CLI command will run with the desired profile:

```bash
aws s3 ls s3://mybucketname/ --profile myprofilename
```

#### Confirm credentials are working

To confirm your AWS credentials are working as expected, you can run the following AWS CLI command:

```bash
aws sts get-caller-identity
```

This will output the currently logged in user and AWS account. 

### Copy data to PO.DAAC using the AWS CLI

How to list data in S3:
```bash
# List buckets (You may not have permissions to run this command)
aws s3 ls
# List items in a bucket location
aws s3 ls s3://mybucketname/prefix/
# Recursively list all items in a bucket
aws s3 ls s3://mybucketname --recursive
```

How to copy data to S3:
```bash
# Copy a single file to an AWS S3 location
aws s3 cp /path/to/file.nc s3://mybucketname/prefix/
# Recursively copy all files in a folder to an AWS S3 location
aws s3 cp /path/to/ s3://mybucketname/prefix/ --recursive
# Use the dryrun flag to see a preview of what will be copied before it's actually copied.
aws s3 cp /path/to/ s3://mybucketname/prefix/ --recursive --dryrun
# Sync files from folder to an AWS S3 location
aws s3 sync /path/to/ s3://mybucketname/prefix/
# Sync files with ".txt" extension from folder to an AWS S3 location
aws s3 sync /path/to/ s3://mybucketname/prefix/ --exclude "*" --include "*.txt"
```
### Copy data to PO.DAAC using Python


```python
import boto3
s3 = boto3.client('s3')

# Upload a single file to S3
s3.upload_file('/path/to/file.nc', 'mybucketname', 'prefix/file.nc')

# List files in bucket`
s3_response = s3.list_objects_v2(
    Bucket='mybucketname',
    Prefix='prefix/'
)
```

## Automate Credential Rotation

These instructions assume that you have an existing SRV account with access keys installed in your local AWS credentials file, which is typically stored at this path: `~/.aws/credentials`.

This example requires Python 3 and the [boto3](https://boto3.amazonaws.com/v1/documentation/api/latest/guide/quickstart.html) python package.

### MACOS/LINUX

Automate the periodic retrieval and installation of your PODAAC-managed s3 access keys using a local cron job.

Clone this repository and copy the python script [rotate_upload_access_keys.py](rotate_upload_access_keys.py) to the following path: `~/.aws/rotate_upload_access_keys.py`.

Start your local crontab editor with `crontab -e`. Add the following line; then save the file.

```
30 0 * * * python3 $HOME/.aws/rotate_upload_access_keys.py SRV-podaac-dev-swot >> $HOME/.aws/rotate_upload_access_keys.log
```

This example crontab entry executes [a python script](rotate_upload_access_keys.py) once per day at 12:30 AM local time. The script checks for new access keys for the `SRV-podaac-dev-swot` account and updates the corresponding entry inside ~/.aws/credentials when necessary.

Output from each run is piped to a log file here: `$HOME/.aws/rotate_upload_access_keys.log`

### WINDOWS

@jjmcnelis to update this ASAP with an equivalent example using Windows task scheduler.
