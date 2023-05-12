import asyncio
import websockets
import json

MY_TOKEN = "eyJhbGciOiJSUzI1NiJ9.eyJuYW1lIjoiT0RJTl9NT05JVE9SIiwiZW1haWwiOiJqLmhhbWFubkBiYW5raGF1cy1zY2hlaWNoLmRlIiwic3ViIjoiT0RJTl9NT05JVE9SIiwianRpIjoiNWRhYTM0Y2QtYjM2MC0xMWViLWJmMzAtZGI5ZjgyN2Y1NDk3IiwiaWF0IjoxNjgwMDg0MjQ0LCJleHAiOjE3MTE2MjAyNDR9.zwKen1ySSEAAX2YJwpdTttsaaxB2nZ8lhAGQXh3BQBE_THxDw5CiZlS0gYqnttLhQB-tsVom1U6WvSpmR_jr9yw9qIM0qQF8BsjTVg1Fjnn8sK_v_V7RQ1cwd4qW7lIMT8OzbI_6gzyXT8HmJZMqDl70B5MB4zqnE2kUHi5EkP2U4fr0qZVXwpDDJKmNs0Ft3yqJylxUQLaS7pPGgBD391HvmfwPkHkTj5ecUMAwG0CcoBSBVxrCfY4ZarvY0EijRDYQgOrtySqZHnQ_GqYOMP_2i5rWtbfLUG2r-x4P_5N6AhuyscGol2UAFAy2UZ_dI-lI5zsc_pf1pSBVCpaWew"
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
            if len(memory_array) == 0:
                memory_array.append(curr_res)

            elif len(memory_array_to_be_printed)!=0:
                memory_array_to_be_printed.append(curr_res)
                #S3 push
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

asyncio.run(get_prices(instrument='BTCEUR'))