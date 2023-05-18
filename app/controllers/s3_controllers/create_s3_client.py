import asyncio

import boto3


def create_s3_client():
    try:
        client = boto3.client(service_name='s3',
                              region_name='eu-central-1')
        return client
    except Exception as e:
        print(f'Faced an Error while creating the S3 Client: {e}')
        print('Trying again to create the s3 client again')
        asyncio.run(create_s3_client())
