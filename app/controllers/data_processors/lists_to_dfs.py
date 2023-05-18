import pandas as pd


def lists_to_dfs(sides_lists: dict, instrument: str) -> dict:
    buy_df = pd.DataFrame([element[0] for element in sides_lists['buy']], columns=list(sides_lists['buy'][0][0].keys()))
    sell_df = pd.DataFrame([element[0] for element in sides_lists['sell']], columns=list(sides_lists['sell'][0][0].keys()))
    buy_df = buy_df[buy_df['instrument'] == instrument].groupby("quantity")
    sell_df = sell_df[sell_df['instrument'] == instrument].groupby("quantity")
    return {'buy_df': buy_df, 'sell_df': sell_df}
