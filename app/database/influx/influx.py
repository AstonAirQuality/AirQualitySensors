import os

from influxdb_client import InfluxDBClient, WriteOptions, Point

from app.api_wrappers.base_wrapper import BaseSensor
from app.api_wrappers.plume_wrapper import PlumeSensor
from app.api_wrappers.sensor_community_wrapper import SCSensor
from app.api_wrappers.zephyr_wrapper import ZephyrSensor

INFLUX_URL = os.getenv("INFLUXDB_V2_URL")
ORGANISATION = os.getenv("INFLUXDB_V2_ORG")
TOKEN = os.getenv("INFLUXDB_V2_TOKEN")
BUCKET_MAPPINGS = {"plume": PlumeSensor, "zephyr": ZephyrSensor, "sensor_community": SCSensor}


class Influx:

    @staticmethod
    def write(bucket: str, sensor_data: BaseSensor, measurement="pollutants"):
        writer = InfluxDBClient(url=INFLUX_URL, org=ORGANISATION, token=TOKEN).write_api(
            write_options=WriteOptions(batch_size=50_000, flush_interval=10_000))
        for entry in sensor_data:
            record_ = Point(measurement).time(sensor_data)
            # add fields to record
            for k, v in entry.fields.items():
                record_.field(k, v)
            # add tags to record
            for k, v in entry.tags.items():
                record_.tag(k, v)
            writer.write(bucket=bucket, record=record_)
        # flush contents of writer to database
        writer.flush()

    @staticmethod
    def read(bucket, start, end) -> BaseSensor:
        class_: BaseSensor = BUCKET_MAPPINGS[bucket]
        pass
