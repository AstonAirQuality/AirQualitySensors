import copy
import datetime
import random

from influxdb_client import InfluxDBClient

from app.api_wrappers.plume_wrapper import PlumeWrapper
from app.api_wrappers.zephyr_wrapper import ZephyrWrapper
from app.influx import Influx
from app.influx import InfluxQueryBuilder

INFLUX_URL = "http://0.0.0.0:8086"
INFLUX_ORG = "aston"
INFLUX_TOKEN = "2UVwEBfD4Kj5FrN5WJHyxcDvw73EfL5RV1IpGE4zv14rIR2RAY-jMFkopjk1_iamFfcwwsHHND2R1Bn4-9mQSA=="
client = InfluxDBClient(url=INFLUX_URL, org=INFLUX_ORG, token=INFLUX_TOKEN)
ZEPHYR_USERNAME = "AstonUniversity"
ZEPHYR_PASSWORD = "Xo08R83d43e0Kk6"

SC_USERNAME = "190102421@aston.ac.uk"
SC_PASSWORD = "RiyadtheWizard"

PLUME_EMAIL = "180086320@aston.ac.uk"
PLUME_PASSWORD = "aston1234"


def write_plume_to_influx():
    pw = PlumeWrapper(PLUME_EMAIL, PLUME_PASSWORD, 85)
    sensors = pw.get_sensors(start=datetime.datetime(2020, 1, 1),
                             end=datetime.datetime(2022, 1, 1),
                             sensors=pw.get_sensor_ids())
    for sensor in sensors:
        Influx.write("plume", sensor.get_writable(), client=client)


def simulate_60_plume_sensors():
    pw = PlumeWrapper(PLUME_EMAIL, PLUME_PASSWORD, 85)
    sensors = pw.get_sensors(start=datetime.datetime(2020, 1, 1),
                             end=datetime.datetime(2022, 1, 1),
                             sensors=pw.get_sensor_ids())
    choices = list(sensors)
    duplicates = []
    for i in range(60 - len(choices)):
        duplicate = copy.deepcopy(random.Random().choice(choices))
        duplicate.id += i  # modify the id
        duplicates.append(duplicate)

    len(duplicates)
    for sensor in duplicates:
        Influx.write("plume", sensor.get_writable(), client=client)


def write_zephyr_to_influx():
    zw = ZephyrWrapper(ZEPHYR_USERNAME, ZEPHYR_PASSWORD)
    sensors = zw.get_sensors(start=datetime.datetime(2020, 1, 1),
                             end=datetime.datetime(2022, 1, 1),
                             sensors=zw.get_sensor_ids(),
                             slot="B")
    for sensor in sensors:
        print(sensor.id)
        Influx.write("zephyr", sensor.get_writable(), client=client)


def read_plume_from_influx():
    query = InfluxQueryBuilder("plume").range()
    sensors = Influx.read(query, client=client)
    for sensor in sensors:
        print(sensor)


def read_zephyr_from_influx():
    query = InfluxQueryBuilder("zephyr").range()
    sensors = Influx.read(query, client=client)
    for sensor in sensors:
        print(sensor)


def find_entries_in_radius():
    # find entries within 20 miles of aston
    query = InfluxQueryBuilder("zephyr").range() \
        .measurement("air_quality") \
        .radius(52.48721619374425, -1.8883056239390839, 20.00)
    sensors = Influx.read(query, client=client)
    for sensor in sensors:
        print(sensor)


def find_entries_in_polygon():
    query = InfluxQueryBuilder("plume").range().measurement("air_quality").polygon(
        [(52.4989543095144, -1.899145490572091),
         (52.49395849821302, -1.8696651939626507),
         (52.4646598973364, -1.9145645619545333)])

    sensors = Influx.read(query, client=client)
    for sensor in sensors:
        print(sensor)


if __name__ == '__main__':
    print("plume")
    write_plume_to_influx()
    # print("zephyr")
    # write_zephyr_to_influx()
