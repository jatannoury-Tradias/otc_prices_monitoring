import asyncio

import datetime

import boto3
import json
import pandas as pd

from models.defected_price import DefectedPrice



def create_s3_client():
    try:
        client = boto3.client(service_name='s3',
        region_name='eu-central-1')
        return client
    except Exception as e:
        print(f'Faced an Error while creating the S3 Client: {e}')
        print('Trying again to create the s3 client again')
        asyncio.run(create_s3_client())



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



def get_file_keys_from_s3(prefix: str) -> list:
    file_keys = []
    client = create_s3_client()
    bucket_path = 'johnnytestbucket'
    response = client.list_objects_v2(Bucket=bucket_path, Prefix=prefix)
    data = response['Contents']
    for key in data:
        file_keys.append(key['Key'])
    return file_keys

def read_s3_files_content(key: str):
    client = create_s3_client()
    bucket_path = 'johnnytestbucket'
    response = client.get_object(Bucket=bucket_path, Key=key)
    data = response['Body'].read()
    return json.loads(data)


def get_defected_price(side, stream, stream_minus_1, stream_plus_1):
    data = []
    for index, level in enumerate(stream['levels'][side]):
        curr_price = level["price"]
        old_price = stream_minus_1["levels"][side][index]['price']
        new_price =stream_plus_1["levels"][side][index]['price']
        diff_with_old = (curr_price - old_price) * 10_000 / (0.5 * (curr_price + old_price))
        diff_with_new = (curr_price - new_price) * 10_000 / (0.5 * (curr_price + new_price))
        defected_price = DefectedPrice()
        defected_price.instrument = stream['instrument']
        defected_price.quantity = stream_minus_1['levels'][side][index]['quantity']
        defected_price.difference_with_old = diff_with_old
        defected_price.difference_with_new = diff_with_new
        defected_price.price_timestamp = stream['timestamp']
        data.append([defected_price.__dict__])
    return data

def list_to_df(results) -> pd.DataFrame:
    dataframe = pd.DataFrame([results])
    return dataframe


def s3_data_collector():
    buy = []
    sell = []
    filekeys = get_file_keys_from_s3(prefix='otc_prices_monitoring/talosprices')
    counter = 0
    for filekey in filekeys:
        data = read_s3_files_content(key=filekey)
        stream_minus_1 = data[0]
        stream = data[1]
        stream_plus_1 = data[2]
        current_buy_bids = get_defected_price('buy', stream=stream, stream_minus_1=stream_minus_1, stream_plus_1=stream_plus_1)
        current_sell_bids = get_defected_price('sell', stream=stream, stream_minus_1=stream_minus_1, stream_plus_1=stream_plus_1)
        buy.extend(current_buy_bids)
        sell.extend(current_sell_bids)
        counter +=1
        print(counter)
    list_to_df(buy)
    print(sell)



s3_data_collector()



