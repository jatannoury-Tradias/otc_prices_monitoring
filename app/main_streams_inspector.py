import asyncio
import orjson
import sys

import websockets

from config.config import ODIN_MONITOR
from app.controllers.s3_controllers.upload_to_s3 import upload_to_s3

ARGUMENTS = sys.argv

MY_TOKEN = ODIN_MONITOR

MONITOR_URI = "wss://otcapp.tradias.de/otc/monitor/ws"

headers = {
    'x-token-id': MY_TOKEN
}


async def get_prices(price_channel, instrument: str) -> None:
    memory_array = []
    memory_array_to_be_printed = []
    async with websockets.connect(uri=MONITOR_URI, extra_headers=headers) as websocket:
        await websocket.send(orjson.dumps({"type": "subscribe",
                                         "channelname": price_channel,
                                         "instrument": instrument,
                                         "heartbeat": True}))
        while True:
            curr_res = orjson.loads(await websocket.recv())
            # print(curr_res)
            if "levels" not in curr_res:
                continue
            if price_channel != 'prices' and curr_res['event'] != "Talos_All":
                continue
            if len(memory_array) == 0:
                memory_array.append(curr_res)

            elif len(memory_array_to_be_printed) != 0:
                memory_array_to_be_printed.append(curr_res)
                upload_to_s3(memory_array_to_be_printed, price_channel)
                memory_array_to_be_printed = []
                memory_array = []
            else:
                stream_minus_1 = memory_array[-1]
                for index, level in enumerate(curr_res['levels']["buy"]):
                    new_price = level["price"]
                    old_price = stream_minus_1['levels']['buy'][index]['price']
                    if abs(new_price - old_price) * 10_000 / (0.5 * (new_price + old_price)) > 20:
                        memory_array_to_be_printed.append(stream_minus_1)
                        memory_array_to_be_printed.append(curr_res)
                        break
                if len(memory_array_to_be_printed) != 0:
                    continue
                for index, level in enumerate(curr_res['levels']["sell"]):
                    new_price = level["price"]
                    old_price = stream_minus_1['levels']['sell'][index]['price']
                    if abs(new_price - old_price) * 10_000 / (0.5 * (new_price + old_price)) > 20:
                        memory_array_to_be_printed.append(stream_minus_1)
                        memory_array_to_be_printed.append(curr_res)
                        break


async def main(price_channel: str):
    task_1 = asyncio.create_task(get_prices(instrument='BTCEUR', price_channel=price_channel))
    task_2 = asyncio.create_task(get_prices(instrument='ETHEUR', price_channel=price_channel))
    await asyncio.gather(task_1, task_2)


if __name__ == "__main__":
    if ARGUMENTS[1] == 'talos':
        print("Starting on Talos")
        asyncio.run(main(price_channel='talosprices'))
    else:
        print('Starting on Prices')
        asyncio.run(main(price_channel='prices'))
