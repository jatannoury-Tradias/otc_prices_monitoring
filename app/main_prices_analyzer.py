import asyncio

from app.controllers.prices_analyzer import prices_analyzer

folder_path = 'otc_prices_monitoring/prices'


async def main():
    task1 = asyncio.create_task(prices_analyzer(prefix=folder_path, instrument='BTCEUR'))
    # task2 = asyncio.create_task(prices_analyzer(prefix=folder_path, instrument='ETHEUR'))
    await asyncio.gather(task1)


if __name__ == "__main__":
    asyncio.run(main())
