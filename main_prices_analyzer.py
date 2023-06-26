import asyncio

from app.controllers.prices_analyzer import prices_analyzer


async def main(instrument: str, folder_path: str):
    task1 = asyncio.create_task(prices_analyzer(prefix=folder_path, instrument=instrument, limit=1000))
    await asyncio.gather(task1)


if __name__ == "__main__":
    days = [20]
    streams = ['talosprices']
    instruments = ['ETHEUR', 'BTCEUR']

    for day in days:
        for stream in streams:
            for instrument in instruments:
                s3_path = f'otc_prices_monitoring/{stream}/2023-06-{day}'
                asyncio.run(main(instrument=instrument, folder_path=s3_path))
