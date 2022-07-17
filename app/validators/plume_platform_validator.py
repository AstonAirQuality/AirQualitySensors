import re

from app.models.plume_platform import PlumePlatform


class InvalidSerialNumberException(Exception):
    pass


class InvalidEmailException(Exception):
    pass


class PlumePlatformValidator:
    def __init__(self):
        self.email = re.compile("(?:[a-z0-9!#$%&'*+/=?^_`{|}~-]+(?:\\.[a-z0-9!#$%&'*+/=?^_`{|}~-]+)*|\"(?:"
                                "[\\x01-\\x08\\x0b\\x0c\\x0e-\\x1f\\x21\\x23-\\x5b\\x5d-\\x7f]|\\\\[\\x01-\\x09\\x0b\\x0c\\x0e-\\x7f"
                                "])*\")@(?:(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?|\\[(?:(?:25[0-5]|2"
                                "[0-4][0-9]|[01]?[0-9][0-9]?)\\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?|[a-z0-9-]*[a-z0-9]:(?:[\\"
                                "x01-\\x08\\x0b\\x0c\\x0e-\\x1f\\x21-\\x5a\\x53-\\x7f]|\\\\[\\x01-\\x09\\x0b\\x0c\\x0e-\\x7f])+)\\])")

    def is_valid(self, plume: PlumePlatform) -> bool:
        if len(plume.serial_number.split(":")) != 6:
            raise InvalidSerialNumberException("Serial number needs to be in the following format: XX:XX:XX:XX:XX:XX")

        if not self.email.match(plume.email):
            raise InvalidEmailException("Email not valid format")

        return True
