import boto3
from botocore.exceptions import ClientError
import os
import traceback

def upload_file(file_name, bucket='jmattfong-halloween-public', object_name=None):
    """Upload a file to an S3 bucket

    :param file_name: File to upload
    :param bucket: Bucket to upload to
    :param object_name: S3 object name. If not specified then file_name is used
    :return: S3 URL
    """

    # If S3 object_name was not specified, use file_name
    if object_name is None:
        object_name = os.path.basename(file_name)

    # Upload the file
    print(f'Uploading image {file_name}')
    s3_client = boto3.client('s3')
    try:
        response = s3_client.upload_file(file_name, bucket, object_name)
    except ClientError as e:
        # printing stack trace
        traceback.print_exc()
        return ''
    file_basename = os.path.basename(file_name)
    return f'https://jmattfong-halloween-public.s3.us-west-2.amazonaws.com/{file_basename}'
