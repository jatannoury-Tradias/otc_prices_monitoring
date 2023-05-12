import asyncio
import websockets
import json

from s3_controller import upload_to_s3

MY_TOKEN = ""
ENVIRONMENT = "otcapp"
PROTOCOL = "wss"

URI = f"{PROTOCOL}://{ENVIRONMENT}.tradias.de/otc/monitor/ws"

headers = {
    "x-token-id": MY_TOKEN
}

async def get_prices(instrument: str) -> None:
    memory_array=[]
    memory_array_to_be_printed=[]
    async with websockets.connect(uri=URI, extra_headers=headers) as websocket:
        await websocket.send(json.dumps({
            "type": "subscribe",
            "channelname": "talosprices",
            "instrument": instrument,
            "heartbeat": True
        }))
        while True:
            curr_res = json.loads(await websocket.recv())
            print(curr_res)
            if "levels" not in curr_res:
                continue
            if curr_res['event'] != "Talos_All":
                continue
            if len(memory_array) == 0:
                memory_array.append(curr_res)

            elif len(memory_array_to_be_printed)!=0:
                memory_array_to_be_printed.append(curr_res)
                upload_to_s3(memory_array_to_be_printed)
                memory_array_to_be_printed=[]
                memory_array = []
            else:
                stream_minus_1 = memory_array[-1]
                for index,level in enumerate(curr_res['levels']["buy"]):
                    new_price = level["price"]
                    old_price = stream_minus_1['levels']['buy'][index]['price']
                    if abs(new_price - old_price) * 10_000 / (0.5 * (new_price+old_price)) > 0.000001:
                        memory_array_to_be_printed.append(stream_minus_1)
                        memory_array_to_be_printed.append(curr_res)
                        break
                if len(memory_array_to_be_printed) != 0:
                    continue
                for index,level in enumerate(curr_res['levels']["sell"]):
                    new_price = level["price"]
                    old_price = stream_minus_1['levels']['sell'][index]['price']
                    if abs(new_price - old_price) * 10_000 / (0.5 * (new_price+old_price)) > 0.000001:
                        memory_array_to_be_printed.append(stream_minus_1)
                        memory_array_to_be_printed.append(curr_res)
                        break
async def main():
    task_1 = asyncio.create_task(get_prices(instrument='BTCEUR'))
    task_2 = asyncio.create_task(get_prices(instrument='ETHEUR'))
    await asyncio.gather(task_1, task_2)

asyncio.run(main())
