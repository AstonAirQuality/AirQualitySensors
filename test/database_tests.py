import datetime

from influxdb_client import InfluxDBClient

from app.api_wrappers.plume_wrapper import PlumeWrapper
from app.database.influx.influx import Influx

INFLUX_URL = "http://127.0.0.1:8086"
INFLUX_ORG = "aston"
INFLUX_TOKEN = "2UVwEBfD4Kj5FrN5WJHyxcDvw73EfL5RV1IpGE4zv14rIR2RAY-jMFkopjk1_iamFfcwwsHHND2R1Bn4-9mQSA=="

PLUME_EMAIL = "180086320@aston.ac.uk"
PLUME_PASSWORD = "aston1234"


def write_plume_to_influx():
    pw = PlumeWrapper(PLUME_EMAIL, PLUME_PASSWORD, 85)
    sensors = pw.get_sensors(start=datetime.datetime(2022, 1, 1),
                             end=datetime.datetime(2022, 1, 31),
                             sensors=pw.get_sensor_ids())
    for sensor in sensors:
        Influx.write("plume", sensor, client=InfluxDBClient(url=INFLUX_URL, org=INFLUX_ORG, token=INFLUX_TOKEN))
