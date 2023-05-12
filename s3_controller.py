import asyncio

import datetime

import boto3
import json



def create_s3_client():
    try:
        client = boto3.client(service_name='s3',
        region_name='eu-central-1')
        return client
    except Exception as e:
        print(f'Faced an Error while creating the S3 Client: {e}')
        print('Trying again to create the s3 client again')
        asyncio.run(create_s3_client())



def upload_to_s3(file_object):
    client = create_s3_client()
    bucket_path = 'johnnytestbucket'
    file_name = f'otc_prices_monitoring/{datetime.datetime.utcnow().strftime("%Y-%m-%d")}/{datetime.datetime.utcnow().strftime("%H:%M:%S")}.json'
    file_object = json.dumps(file_object)
    print(f'Filename = {file_name}')
    try:
        response = client.put_object(Body=file_object, Bucket=bucket_path, Key=file_name)
        print(f'Uploaing {file_name} to bucket response {response}')
    except Exception as e:
        print(f'Upload Not Completed du to an error')
        raise e
