from app.controllers.s3_controllers.upload_to_s3 import upload_to_s3
from app.tools.websocket_helper import WebsocketHelper
import datetime

MAX_BASIS_POINTS_ALLOWED = 20
BASIS_POINTS_FACTOR = 10_000
MIN_LEVELS_ALLOWED = 6

async def prices_selector(websocket: WebsocketHelper, price_channel):
    memory_array = None
    memory_array_to_be_printed = []
    while True:
        curr_res = await websocket.receiver_queue.get()
        if "levels" not in curr_res:
            continue
        if len(curr_res['levels']['buy']) < MIN_LEVELS_ALLOWED or len(curr_res['levels']['sell']) < MIN_LEVELS_ALLOWED:
            upload_to_s3(curr_res, 'defected')
        if price_channel == 'prices' and curr_res['source'] != "Talos_All":
            continue
        if price_channel == 'talos' and curr_res['event'] != "Talos_All":
            continue
        if not memory_array:
            memory_array = curr_res

        elif len(memory_array_to_be_printed) != 0:
            memory_array_to_be_printed.append(curr_res)
            upload_to_s3(memory_array_to_be_printed, price_channel)
            memory_array_to_be_printed = []
            memory_array = None
        else:
            stream_minus_1 = memory_array
            for index, level in enumerate(curr_res['levels']["buy"]):
                new_price = level["price"]
                old_price = stream_minus_1['levels']['buy'][index]['price']
                if abs(new_price - old_price) * BASIS_POINTS_FACTOR / (
                        0.5 * (new_price + old_price)) > MAX_BASIS_POINTS_ALLOWED:
                    memory_array_to_be_printed.append(stream_minus_1)
                    memory_array_to_be_printed.append(curr_res)
                    break
            if len(memory_array_to_be_printed) != 0:
                continue
            for index, level in enumerate(curr_res['levels']["sell"]):
                new_price = level["price"]
                old_price = stream_minus_1['levels']['sell'][index]['price']
                if abs(new_price - old_price) * BASIS_POINTS_FACTOR / (
                        0.5 * (new_price + old_price)) > MAX_BASIS_POINTS_ALLOWED:
                    memory_array_to_be_printed.append(stream_minus_1)
                    memory_array_to_be_printed.append(curr_res)
                    break
            memory_array = curr_res
