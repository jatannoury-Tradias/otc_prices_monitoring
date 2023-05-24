import asyncio

from app.controllers.prices_analyzer import prices_analyzer


async def main(instrument: str, folder_path: str):
    task1 = asyncio.create_task(prices_analyzer(prefix=folder_path, instrument=instrument, limit=1000))
    await asyncio.gather(task1)


if __name__ == "__main__":
    instruments = ['BTCEUR', 'ETHEUR']
    days = [22, 23, 24]
    streams = ['talosprices', 'prices']

    for day in days:
        for stream in streams:
            for instrument in instruments:
                asyncio.run(main(instrument=instrument, folder_path=f'otc_prices_monitoring/{stream}/2023-05-{day}'))



