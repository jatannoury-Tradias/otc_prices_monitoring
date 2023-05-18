import datetime

from matplotlib import pyplot as plt


def defected_prices_data_plotter(dfs: dict, prefix: str, instrument: str):
    fig, axes = plt.subplots(4, 4, figsize=(10, 8))
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
        ax.set_xlabel('Price Timestamp')
        ax.set_ylabel('Difference')
        ax.tick_params(axis='x', rotation=10, labelsize=6)
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
        ax.set_xlabel('Price Timestamp')
        ax.set_ylabel('Difference')
        ax.tick_params(axis='x', rotation=0, labelsize=8)
        ax.xaxis.set_major_locator(plt.MaxNLocator(5))
    legends = ['Difference with old', 'Difference with new']
    fig.legend(legends, loc='lower right', ncol=len(legends))
    # plt.legend()
    # Adjust spacing between subplots
    fig.suptitle(f'{prefix[22:].upper()} {instrument} channel stream analysis')
    plt.subplots_adjust(wspace=0.4, hspace=0.6)
    # plt.autoscale()
    plt.tight_layout()

    # Display the plot
    plt.show()
