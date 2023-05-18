import datetime
import json

from app.controllers.s3_controllers.create_s3_client import create_s3_client


def upload_to_s3(file_object, channel_name):
    client = create_s3_client()
    bucket_path = 'johnnytestbucket'
    file_name = f'otc_prices_monitoring/{channel_name}/{datetime.datetime.utcnow().strftime("%Y-%m-%d")}/{datetime.datetime.utcnow().strftime("%H:%M:%S")}.json'
    file_object = json.dumps(file_object)
    print(f'Filename = {file_name}')
    try:
        response = client.put_object(Body=file_object, Bucket=bucket_path, Key=file_name)
        print(f'Uploaing {file_name} to bucket response {response}')
    except Exception as e:
        print(f'Upload Not Completed du to an error')
        raise e
