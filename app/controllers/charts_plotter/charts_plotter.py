import datetime
import os.path

from matplotlib import pyplot as plt
from app.config.paths import DATA_PATH


def defected_prices_data_plotter(dfs: dict, prefix: str, instrument: str):
    fig, axes = plt.subplots(4, 4, figsize=(20, 10))
    for i, (quantity, group) in enumerate(dfs['buy_df']):
        # Calculate the position of the current subplot
        row = i // 4
        col = i % 4

        # Select the current subplot
        ax = axes[row, col]
        # Plot the data in the current subplot
        group['price_timestamp'] = group['price_timestamp'].apply(
            lambda element: datetime.datetime.strptime(element, "%Y-%m-%dT%H:%M:%S.%fZ").strftime("%H:%M:%S"))
        ax.scatter(group['price_timestamp'], group['difference_with_old'], label='Difference with Old')
        ax.scatter(group['price_timestamp'], group['difference_with_new'], label='Difference with New')

        # Set title and labels for the current subplot
        ax.set_title(f'Buy Quantity: {quantity}')
        # ax.set_xlabel('Price Timestamp')
        ax.set_ylabel('Difference (BPS)')
        ax.tick_params(axis='x', rotation=0, labelsize=8)
        ax.xaxis.set_major_locator(plt.MaxNLocator(5))

    for i, (quantity, group) in enumerate(dfs['sell_df']):
        # Calculate the position of the current subplot
        row = i // 4 + 2 if i // 4 + 2 < 4 else 3
        col = i % 4

        # Select the current subplot
        ax = axes[row, col]
        group['price_timestamp'] = group['price_timestamp'].apply(
            lambda element: datetime.datetime.strptime(element, "%Y-%m-%dT%H:%M:%S.%fZ").strftime("%H:%M:%S"))
        ax.scatter(group['price_timestamp'], group['difference_with_old'], label='Difference with Old')
        ax.scatter(group['price_timestamp'], group['difference_with_new'], label='Difference with New')

        # Set title and labels for the current subplot
        ax.set_title(f'Sell Quantity: {quantity}')
        # ax.set_xlabel('Price Timestamp')
        ax.set_ylabel('Difference (BPS)')
        ax.tick_params(axis='x', rotation=0, labelsize=8)
        ax.xaxis.set_major_locator(plt.MaxNLocator(5))
    legends = ['Difference with old', 'Difference with new']
    fig.legend(legends, loc='lower right', ncol=len(legends))
    # plt.legend()
    # Adjust spacing between subplots
    fig.suptitle(f'{prefix[22:].upper()} {instrument} channel stream analysis')
    # plt.subplots_adjust(wspace=0.1, hspace=0.1)
    fig.subplots_adjust(left=0.05, bottom=0.1, right=0.95, top=0.9, wspace=0.2, hspace=0.43)
    plt.autoscale()
    # plt.tight_layout()
    date = prefix.split('/')[2]
    stream = prefix.split('/')[1]
    filepath = f'{DATA_PATH}\\{stream.upper()}-{date}-{instrument}-channel stream analysis.svg'
    # Display the plot
    plt.savefig(filepath, format='svg', dpi=300)
    # plt.show()
