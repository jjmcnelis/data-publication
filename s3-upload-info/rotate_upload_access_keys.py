#!/usr/bin/env python3
import os, sys, json, boto3, datetime, argparse, configparser
from botocore.exceptions import ClientError, ProfileNotFound

default_aws_credentials_file = os.path.join(os.path.expanduser("~"), ".aws/credentials")

default_contact_message = 'Please contact podaac@podaac.jpl.nasa.gov for assistance.'


def get_timestamp():
    return str(datetime.datetime.utcnow()).split(".")[0]


def update_local_creds(profile_name: str, 
                       aws_access_key_id: str, 
                       aws_secret_access_key: str, 
                       aws_credentials_file: str=default_aws_credentials_file):
    config = configparser.RawConfigParser(allow_no_value=True)
    try:
        config.read(aws_credentials_file)
        if config.get(profile_name, 'aws_access_key_id')==aws_access_key_id:
            sys.exit(print(f"[{get_timestamp()}]", 'NO CHANGES, Local credentials for ', f'"{profile_name}"', ' are current.'))
        config.set(profile_name, 'aws_access_key_id', aws_access_key_id)
        config.set(profile_name, 'aws_secret_access_key', aws_secret_access_key)            
        with open(aws_credentials_file, 'w+') as f:
            config.write(f)
    except Exception as e:
        sys.exit(print(f"[{get_timestamp()}]", f'ERROR! Local credentials for "{profile_name}" may be expired.', default_contact_message))
    else:
        print(f"[{get_timestamp()}]", 'KEYS ROTATED, Local credentials for ', f'"{profile_name}"', ' were rotated successfully.')


def get_active_creds(profile_name: str, region_name: str="us-east-1"):
    try:
        session = boto3.session.Session(profile_name=profile_name)
        client = session.client(service_name='secretsmanager', region_name=region_name)
        response = client.get_secret_value(SecretId=f"User_{profile_name}_AccessKey")
        secret = json.loads(response['SecretString'])
        secret['profile_name'] = secret.pop('UserName')
        secret['aws_access_key_id'] = secret.pop('AccessKeyId')
        secret['aws_secret_access_key'] = secret.pop('SecretAccessKey')
        created, status = secret['CreateDate'], secret['Status']
        del secret['CreateDate'], secret['Status']
    except ProfileNotFound as e:
        sys.exit(print(f"[{get_timestamp()}]", f'ERROR! Local credentials are not stored for "{profile_name}".', default_contact_message))
    except ClientError as e:
        sys.exit(print(f"[{get_timestamp()}]", f'ERROR! Local credentials for "{profile_name}" are expired or otherwise invalid.', default_contact_message))
    else:
        return secret, created, status


def main(profile_name: str):
    secret, created, status = get_active_creds(profile_name)
    sys.exit(update_local_creds(**secret))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('profile', metavar='Profile name that corresponds to a PODAAC-managed SRV account credential, e.g. "SRV-podaac-dev-swot"', type=str)
    args = parser.parse_args()
    main(args.profile)