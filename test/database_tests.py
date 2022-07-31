import datetime
import os

from influxdb_client import InfluxDBClient

from app.api_wrappers.plume_wrapper import PlumeWrapper
from app.api_wrappers.sensor_community_wrapper import SCWrapper
from app.api_wrappers.zephyr_wrapper import ZephyrWrapper
from app.influx import Influx
from app.influx import InfluxQueryBuilder

INFLUX_URL = "http://0.0.0.0:8086"
INFLUX_ORG = "aston"
INFLUX_TOKEN = "2UVwEBfD4Kj5FrN5WJHyxcDvw73EfL5RV1IpGE4zv14rIR2RAY-jMFkopjk1_iamFfcwwsHHND2R1Bn4-9mQSA=="
client = InfluxDBClient(url=INFLUX_URL, org=INFLUX_ORG, token=INFLUX_TOKEN)

ZEPHYR_USERNAME = os.environ.get("ZEPHYR_USERNAME")
ZEPHYR_PASSWORD = os.environ.get("ZEPHYR_PASSWORD")

SC_USERNAME = os.environ.get("SC_USERNAME")
SC_PASSWORD = os.environ.get("SC_PASSWORD")

PLUME_EMAIL = os.environ.get("PLUME_EMAIL")
PLUME_PASSWORD = os.environ.get("PLUME_PASSWORD")


def write_plume_to_influx():
    pw = PlumeWrapper(PLUME_EMAIL, PLUME_PASSWORD, 85)
    sensors = pw.get_sensors(start=datetime.datetime(2021, 1, 1),
                             end=datetime.datetime(2022, 1, 1),
                             sensors=pw.get_sensor_ids(),
                             timeout=30)
    for sensor in sensors:
        print(sensor.id)
        Influx.write("plume", sensor.get_writable(), client=client)


def write_zephyr_to_influx():
    # data available between 19-09-2021, 20-09-2021
    zw = ZephyrWrapper(ZEPHYR_USERNAME, ZEPHYR_PASSWORD)
    sensors = zw.get_sensors(start=datetime.datetime(2021, 9, 19),
                             end=datetime.datetime(2021, 9, 20),
                             sensors=zw.get_sensor_ids(),
                             slot="B")
    for sensor in sensors:
        print(sensor.id)
        Influx.write("zephyr", sensor.get_writable(), client=client)


def write_sensor_community_to_influx():
    # can only ingest a single data at a time
    scw = SCWrapper(SC_USERNAME, SC_PASSWORD)
    sensors = scw.get_sensors(end=datetime.datetime.today() - datetime.timedelta(days=1),
                              start=datetime.datetime(2021, 10, 18),
                              sensors={'66007': 'SDS011', '66008': 'SHT31'})

    for sensor in sensors:
        print(sensor.id)
        Influx.write("sensor_community", sensor.get_writable(), client=client)


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
    # find entries within 20 miles of Aston university
    query = InfluxQueryBuilder("plume").range().measurement("air_quality").radius(52.48721619374425,
                                                                                  -1.8883056239390839,
                                                                                  20.00)
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
    print("Searching for Plume readings in polygon")
    find_entries_in_polygon()
    print("Searching for Plume readings in radius")
    find_entries_in_radius()
