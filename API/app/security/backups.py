#!/usr/bin/env python3

import boto3, os
from boto3.dynamodb.conditions import Key
from pathlib import Path
import datetime
"""
    Backups manager,
    here is where we can handle and make our backups whenever we want, just calling the function

"""



def make_backup_s3():
    """
    Function to make backups into an S3 Bucket. Designed to store CSV files as security copies.
    Utilizes S3 for its reliability and ease of use.
    """

    # Environment variables for AWS credentials and region
    access_key = "AKIA5IMAAAMYB25B5MXZ"
    secret_access_key = "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"
    region_name = "us-east-1"

    # Create S3 client
    s3_client = boto3.client(
        's3',
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_access_key,
        region_name=region_name
    )

    # S3 bucket name
    bucket_name = 'paus-private-storage'

    # File path to upload and target file name in S3
    file_to_upload = Path('datasets/main_dataset_manager2.csv')
    date = datetime.datetime.now()
    target_key = f'cliente_gestor_backups/tabla_users_{date.day}-{date.month}-{date.year}.csv'

    # Upload the file
    s3_client.upload_file(str(file_to_upload), bucket_name, target_key)
    print(f"File uploaded to S3 as {target_key}")


if __name__ == "__main__":
    make_backup_s3()