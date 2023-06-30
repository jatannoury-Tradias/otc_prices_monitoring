from app.controllers.s3_controllers.upload_to_s3 import upload_to_s3


def check_outbound_levels(price, threshold, channel):
    if price['source'] == 'Talos_All':
        if len(price['levels']['buy']) < threshold or len(
                price['levels']['sell']) < threshold:
            upload_to_s3(price, f'defected_{channel}')
            return True


