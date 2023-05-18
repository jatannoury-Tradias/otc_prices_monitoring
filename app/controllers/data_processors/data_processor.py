from app.controllers.data_processors.get_data_list import get_defected_prices_list
from app.controllers.s3_controllers.get_files_keys import get_file_keys_from_s3
from app.controllers.s3_controllers.read_s3_files_content import read_s3_files_content


def data_processor(prefix: str, limit: int) -> dict:
    buy = []
    sell = []
    counter = 0
    filekeys = get_file_keys_from_s3(prefix=prefix)
    for filekey in filekeys:
        if counter == limit: break
        data = read_s3_files_content(key=filekey)
        stream_minus_1 = data[0]
        stream = data[1]
        stream_plus_1 = data[2]
        current_buy_bids = get_defected_prices_list('buy', stream=stream, stream_minus_1=stream_minus_1,
                                                    stream_plus_1=stream_plus_1)
        current_sell_bids = get_defected_prices_list('sell', stream=stream, stream_minus_1=stream_minus_1,
                                                     stream_plus_1=stream_plus_1)
        buy.extend(current_buy_bids)
        sell.extend(current_sell_bids)
        counter += 1
    return {'buy': buy, 'sell': sell}
