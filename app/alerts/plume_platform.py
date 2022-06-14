from app.api_wrappers.plume_wrapper import PlumeWrapper


class PlumePlatform:

    def __init__(self, serial_number):
        self.serial_number = serial_number

    def save_plume_platform(self):
        pass

    @property
    def plume_platform_id(self):
        # TODO: only access api if sensor is not saved in a database
        plume_platform_id = next(PlumeWrapper.env_factory().convert_serial_number_to_platform_id((self.serial_number,)))

    @property
    def platform_id(self):
        # TODO: Get from database
        pass
