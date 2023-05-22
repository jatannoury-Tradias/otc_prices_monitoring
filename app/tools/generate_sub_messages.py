def generate_sub_messages(price_channels: list[str], instruments: list[str]) -> list:
    sub_messages = []
    for price_channel in price_channels:
        for instrument in instruments:

            message = {"type": "subscribe",
                       "channelname": price_channel,
                       "instrument": instrument,
                       "heartbeat": True}
            sub_messages.append(message)
    return sub_messages
