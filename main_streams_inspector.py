import asyncio
import sys

from app.tools.generate_sub_messages import generate_sub_messages
from app.tools.get_headers import get_headers
from app.tools.websocket_helper import WebsocketHelper
from app.controllers.prices_selector import prices_selector



ARGUMENTS = sys.argv

MONITOR_URI = "wss://otcapp.tradias.de/otc/monitor/ws"


async def main_get_prices(price_channel, instrument: str, headers) -> None:
    websocket = WebsocketHelper(url=MONITOR_URI, name=f'{price_channel}-{instrument}-websocket')
    messages = generate_sub_messages(price_channels=[price_channel], instruments=[instrument])
    await asyncio.gather(
        websocket.keep_open(extra_messages=messages, print_response=False, get_extra_headers=headers),
        prices_selector(websocket=websocket, price_channel=price_channel))





async def main(price_channel: str):
    task_1 = asyncio.create_task(main_get_prices(instrument='BTCEUR', price_channel=price_channel, headers=get_headers))
    task_2 = asyncio.create_task(main_get_prices(instrument='ETHEUR', price_channel=price_channel, headers=get_headers))
    await asyncio.gather(task_1, task_2)


if __name__ == "__main__":
    try:
        if ARGUMENTS[1] == 'talos':
            print("Starting on Talos")
            asyncio.run(main(price_channel='talosprices'))
        else:
            print('Starting on Prices')
            asyncio.run(main(price_channel='prices'))
    except Exception as e:
        print(e)

