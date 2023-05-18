from app.controllers.charts_plotter.charts_plotter import defected_prices_data_plotter
from app.controllers.data_processors.data_processor import data_processor
from app.controllers.data_processors.lists_to_dfs import lists_to_dfs


async def prices_analyzer(prefix: str, instrument: str):
    data_lists = data_processor(prefix=prefix, limit=30)
    dataframes = lists_to_dfs(sides_lists=data_lists, instrument=instrument)
    defected_prices_data_plotter(dfs=dataframes, prefix=prefix, instrument=instrument)


# if __name__ == "__main__":
#     folder_path = 'otc_prices_monitoring/prices'
#     inst = 'BTCEUR'
#     prices_analyzer(prefix=folder_path, instrument=inst)


