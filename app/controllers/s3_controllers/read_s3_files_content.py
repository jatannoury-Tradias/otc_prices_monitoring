import json

from app.controllers.s3_controllers.create_s3_client import create_s3_client


def read_s3_files_content(key: str):
    client = create_s3_client()
    bucket_path = 'johnnytestbucket'
    response = client.get_object(Bucket=bucket_path, Key=key)
    data = response['Body'].read()
    return json.loads(data)
