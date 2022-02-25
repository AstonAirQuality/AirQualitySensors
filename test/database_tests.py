import datetime

from influxdb_client import InfluxDBClient

from app.api_wrappers.plume_wrapper import PlumeWrapper
from app.influx import Influx
from app.influx import InfluxQueryBuilder

INFLUX_URL = "http://127.0.0.1:8086"
INFLUX_ORG = "aston"
INFLUX_TOKEN = "2UVwEBfD4Kj5FrN5WJHyxcDvw73EfL5RV1IpGE4zv14rIR2RAY-jMFkopjk1_iamFfcwwsHHND2R1Bn4-9mQSA=="
client = InfluxDBClient(url=INFLUX_URL, org=INFLUX_ORG, token=INFLUX_TOKEN)
PLUME_EMAIL = "180086320@aston.ac.uk"
PLUME_PASSWORD = "aston1234"


def write_plume_to_influx():
    pw = PlumeWrapper(PLUME_EMAIL, PLUME_PASSWORD, 85)
    for i in range(1, 12, 2):
        sensors = pw.get_sensors(start=datetime.datetime(2021, i, 1),
                                 end=datetime.datetime(2021, i + 1, 1),
                                 sensors=pw.get_sensor_ids())
        for sensor in sensors:
            Influx.write("plume", sensor.get_writable(), client=client)


def read_plume_from_influx():
    query = InfluxQueryBuilder("plume").range()
    sensors = Influx.read(query, client=client)
    for sensor in sensors:
        print(sensor)


def find_entries_in_radius():
    # find entries within 20 miles of aston
    query = InfluxQueryBuilder("plume").range() \
        .measurement("air_quality") \
        .radius(52.48721619374425, -1.8883056239390839, 20.00)
    sensors = Influx.read(query, client=client)
    for sensor in sensors:
        print(sensor)


def find_entries_in_polygon():
    query = InfluxQueryBuilder("plume").range() \
        .measurement("air_quality") \
        .polygon([(52.4989543095144, -1.899145490572091),
                  (52.49395849821302, -1.8696651939626507),
                  (52.4646598973364, -1.9145645619545333)])
    sensors = Influx.read(query, client=client)
    for sensor in sensors:
        print(sensor)


if __name__ == '__main__':
    # write_plume_to_influx()
    find_entries_in_polygon()
