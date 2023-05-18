from app.models.defected_price import DefectedPrice


def get_defected_prices_list(side, stream, stream_minus_1, stream_plus_1):
    data = []
    for index, level in enumerate(stream['levels'][side]):
        curr_price = level["price"]
        old_price = stream_minus_1["levels"][side][index]['price']
        new_price = stream_plus_1["levels"][side][index]['price']
        diff_with_old = (curr_price - old_price) * 10_000 / (0.5 * (curr_price + old_price))
        diff_with_new = (curr_price - new_price) * 10_000 / (0.5 * (curr_price + new_price))
        defected_price = DefectedPrice()
        defected_price.instrument = stream['instrument']
        defected_price.quantity = stream_minus_1['levels'][side][index]['quantity']
        defected_price.difference_with_old = diff_with_old
        defected_price.difference_with_new = diff_with_new
        defected_price.price_timestamp = stream['timestamp']
        data.append([defected_price.__dict__])
    return data
