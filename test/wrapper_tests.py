import datetime

from api_wrappers.plume_wrapper import PlumeWrapper
from api_wrappers.sensor_community_wrapper import ScWrapper
from api_wrappers.zephyr_wrapper import ZephyrWrapper

# TODO: Make environment variables
ZEPHYR_USERNAME = "AstonUniversity"
ZEPHYR_PASSWORD = "Xo08R83d43e0Kk6"

SC_USERNAME = "190102421@aston.ac.uk"
SC_PASSWORD = "RiyadtheWizard"

PLUME_EMAIL = "180086320@aston.ac.uk"
PLUME_PASSWORD = "aston1234"


def zephyr_test():
    zw = ZephyrWrapper(ZEPHYR_USERNAME, ZEPHYR_PASSWORD)
    sensors = zw.get_sensors(zw.get_sensor_ids(),
                             start=datetime.datetime(2021, 9, 19),
                             end=datetime.datetime(2021, 9, 20),
                             slot="B")
    for s in sensors:
        print(s.id)
        print(s.dataframe)


def sensor_community_test():
    scw = ScWrapper(SC_USERNAME, SC_PASSWORD)
    sensors = scw.get_sensors({'66007': 'SDS011', '66008': 'SHT31'},
                              datetime.datetime.today() - datetime.timedelta(days=1),
                              startdate=datetime.datetime(2021, 10, 18))

    for sensor in sensors:
        print(sensor.id)
        print(sensor.dataframe)


def plume_test():
    pw = PlumeWrapper(PLUME_EMAIL, PLUME_PASSWORD, 85)
    sens = pw.get_sensors(pw.get_sensor_ids(),
                          start=datetime.datetime(2021, 9, 30),
                          end=datetime.datetime(2021, 10, 13))
    for s in sens:
        print(s.id)
        print(s.dataframe)


if __name__ == '__main__':
    sensor_community_test()
