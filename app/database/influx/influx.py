import os
import datetime as dt
from influxdb_client import InfluxDBClient, WriteOptions, Point, WritePrecision

from app.api_wrappers.base_wrapper import BaseSensor
from app.api_wrappers.plume_wrapper import PlumeSensor
from app.api_wrappers.sensor_community_wrapper import SCSensor
from app.api_wrappers.zephyr_wrapper import ZephyrSensor

BUCKET_MAPPINGS = {"plume": PlumeSensor, "zephyr": ZephyrSensor, "sensor_community": SCSensor}


class Influx:

    @staticmethod
    def get_client(url=os.getenv("INFLUXDB_V2_URL"), org=os.getenv("INFLUXDB_V2_ORG"),
                   token=os.getenv("INFLUXDB_V2_TOKEN")):
        return InfluxDBClient(url=url, org=org, token=token)

    @staticmethod
    def write(bucket: str, sensor_data: BaseSensor, measurement="pollutant", client=None):
        # select static client if no client is specified by the user, helps with testability
        writer = (Influx.get_client() if client is None else client).write_api(
            write_options=WriteOptions(batch_size=50_000, flush_interval=10_000))
        for entry in sensor_data:
            # TODO: Find out why Influx does not insert correctly with UNIX timestamp
            record_ = Point(measurement).time(dt.datetime.fromtimestamp(entry.timestamp))
            # add fields to record
            for k, v in entry.fields.items():
                record_.field(k, v)
            # add tags to record
            for k, v in entry.tags.items():
                record_.tag(k, v)
            writer.write(bucket=bucket, record=record_)
        # flush contents of writer to database
        writer.close()

    @staticmethod
    def read(bucket, start, end) -> BaseSensor:
        class_: BaseSensor = BUCKET_MAPPINGS[bucket]
        pass
