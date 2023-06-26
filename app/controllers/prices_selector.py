from app.config.params import MAX_BASIS_POINTS_ALLOWED, BASIS_POINTS_FACTOR, MIN_OUTBOUND_LEVELS_ALLOWED, \
    MIN_INBOUND_LEVELS_ALLOWED
from app.controllers.inbound_checkers.levels_checker import check_inbound_levels
from app.controllers.outbound_checkers.check_outbound_levels import check_outbound_levels
from app.controllers.s3_controllers.upload_to_s3 import upload_to_s3
from app.tools.websocket_helper import WebsocketHelper


def upload_a_defected_price(price, channel, array):
    array.append(price)
    upload_to_s3(array, channel)


async def prices_selector(websocket: WebsocketHelper, price_channel):
    memory_array = None
    memory_array_to_be_printed = []
    while True:
        curr_res = await websocket.receiver_queue.get()
        if "levels" not in curr_res:
            continue
        if curr_res['event'] == 'prices':
            check_outbound_levels(price=curr_res, threshold=MIN_OUTBOUND_LEVELS_ALLOWED, channel=price_channel)
            continue
        if curr_res['event'] == 'Talos_All':
            check_inbound_levels(price=curr_res, channel=price_channel, threshold=MIN_INBOUND_LEVELS_ALLOWED)
            continue
        if price_channel == 'prices' and curr_res['source'] != "Talos_All":
            continue
        if price_channel == 'talos' and curr_res['event'] != "Talos_All":
            continue
        if not memory_array:
            memory_array = curr_res
        elif len(memory_array_to_be_printed) != 0:
            upload_a_defected_price(price=curr_res, channel=price_channel, array=memory_array_to_be_printed)
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
