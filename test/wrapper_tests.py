import datetime

from app.api_wrappers.plume_wrapper import PlumeWrapper
from app.api_wrappers.sensor_community_wrapper import SCWrapper
from app.api_wrappers.zephyr_wrapper import ZephyrWrapper

# TODO: Make environment variables
ZEPHYR_USERNAME = "AstonUniversity"
ZEPHYR_PASSWORD = "Xo08R83d43e0Kk6"

SC_USERNAME = "190102421@aston.ac.uk"
SC_PASSWORD = "RiyadtheWizard"

PLUME_EMAIL = "180086320@aston.ac.uk"
PLUME_PASSWORD = "aston1234"


def zephyr_test():
    zw = ZephyrWrapper(ZEPHYR_USERNAME, ZEPHYR_PASSWORD)
    sensors = zw.get_sensors(start=datetime.datetime(2021, 9, 19),
                             end=datetime.datetime(2021, 9, 20),
                             sensors=zw.get_sensor_ids(),
                             slot="B")
    for sensor in sensors:
        print(sensor.id)
        print(sensor.dataframe)


def sensor_community_test():
    scw = SCWrapper(SC_USERNAME, SC_PASSWORD)
    sensors = scw.get_sensors(end=datetime.datetime.today() - datetime.timedelta(days=1),
                              start=datetime.datetime(2021, 10, 18),
                              sensors={'66007': 'SDS011', '66008': 'SHT31'})

    for sensor in sensors:
        print(sensor.id)
        print(sensor.dataframe)


def plume_test():
    pw = PlumeWrapper(PLUME_EMAIL, PLUME_PASSWORD, 85)
    sensors = pw.get_sensors(start=datetime.datetime.now() - datetime.timedelta(2),  # day before
                             end=datetime.datetime.now() - datetime.timedelta(1),  # yesterday
                             sensors=pw.get_sensor_ids(),
                             timeout=300)
    for sensor in sensors:
        print(sensor.id)


if __name__ == '__main__':
    # sensor_community_test()
    # zephyr_test()
    plume_test()
