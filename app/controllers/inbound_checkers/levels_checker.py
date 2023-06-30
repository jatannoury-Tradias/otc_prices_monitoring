from app.config.params import MIN_INBOUND_LEVELS_ALLOWED
from app.controllers.s3_controllers.upload_to_s3 import upload_to_s3


def check_inbound_levels(price, channel, threshold):
    if len(price['levels']['buy']) < threshold or len(price['levels']['sell']) < MIN_INBOUND_LEVELS_ALLOWED:
        upload_to_s3(price, f'defected_{channel}')
        return True
