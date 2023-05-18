from app.controllers.s3_controllers.create_s3_client import create_s3_client


def get_file_keys_from_s3(prefix: str) -> list:
    file_keys = []
    client = create_s3_client()
    bucket_path = 'johnnytestbucket'
    response = client.list_objects_v2(Bucket=bucket_path, Prefix=prefix)
    data = response['Contents']
    for key in data:
        file_keys.append(key['Key'])
    return file_keys
