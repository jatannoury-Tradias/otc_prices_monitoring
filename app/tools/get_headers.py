from app.config.config import ODIN_MONITOR


def get_headers():
    return {
        'x-token-id': ODIN_MONITOR
    }
