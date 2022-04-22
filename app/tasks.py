"""
TODO: remove prints
"""

from datetime import datetime, timedelta
import os
from typing import Tuple

from celery import Celery
from celery.schedules import crontab

from api_wrappers.plume_wrapper import PlumeWrapper
from api_wrappers.zephyr_wrapper import ZephyrWrapper
from api_wrappers.base_wrapper import BaseSensor
from api_wrappers.sensor_community_wrapper import SCWrapper
from influx import Influx, InfluxQueryBuilder

app = Celery('tasks', broker=os.environ.get("CELERY_BROKER_URL"), backend=os.environ.get("CELERY_RESULT_BACKEND"))
app.conf.update(result_expires=3600, enable_utc=True, timezone='UTC')


def to_json(sensor: BaseSensor):
    return {"header": sensor.header, "rows": sensor.rows}


def get_dates() -> Tuple[datetime, datetime]:
    """
    :return: start, end -> (now - 1 day), (now - 2 days)
    """
    return datetime.now() - timedelta(1), datetime.now() - timedelta(2)


@app.task(name="read_plume_data")
def read_plume_data(start: float, end: float):
    return [i.to_json() for i in Influx.read(InfluxQueryBuilder("plume").range(start=start, stop=end))]


@app.task(name="read_zephyr_data")
def read_zephyr_data(start: float, end: float):
    return [i.to_json() for i in Influx.read(InfluxQueryBuilder("zephyr").range(start=start, stop=end))]


@app.task(name="read_sensor_community_data")
def read_sensor_community_data(start: float, end: float):
    return [i.to_json() for i in Influx.read(InfluxQueryBuilder("sensor_community").range(start=start, stop=end))]


@app.task(name="daily_zephyr_ingest")
def daily_zephyr_ingest():
    zw = ZephyrWrapper(os.environ.get("ZEPHYR_USERNAME"), os.environ.get("ZEPHYR_PASSWORD"))
    sensors = zw.get_sensors(start=datetime.now() - timedelta(2),  # day before
                             end=datetime.now() - timedelta(1),  # yesterday
                             sensors=zw.get_sensor_ids(),
                             slot="B")
    ids = []
    for sensor in sensors:
        ids.append(sensor.id)
        Influx.write("zephyr", sensor.get_writable())
    return ids


@app.task(name="daily_plume_ingest")
def daily_plume_ingest():
    pw = PlumeWrapper(os.environ.get("PLUME_EMAIL"), os.environ.get("PLUME_PASSWORD"), 85)
    sensors = pw.get_sensors(start=datetime.now() - timedelta(2),  # day before
                             end=datetime.now() - timedelta(1),  # yesterday
                             sensors=pw.get_sensor_ids(),
                             timeout=600)  # 10 minute time out
    ids = []
    for sensor in sensors:
        ids.append(sensor.id)
        Influx.write("plume", sensor.get_writable())
    return ids


@app.task(name="daily_sensor_community_ingest")
def daily_sensor_community_ingest():
    sc = SCWrapper(os.environ.get("SC_USERNAME"), os.environ.get("SC_PASSWORD"))
    sensors = sc.get_sensors(start=datetime.now() - timedelta(2),  # day before
                             end=datetime.now() - timedelta(1),  # yesterday
                             sensors={'66007': 'SDS011', '66008': 'SHT31'})
    ids = []
    for sensor in sensors:
        ids.append(sensor.id)
        Influx.write("sensor_community", sensor.get_writable())
    return ids


@app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    """
    Daily tasks to retrieve sensor data.
    """
    sender.add_periodic_task(crontab(hour=0, minute=0), daily_plume_ingest.s())
    sender.add_periodic_task(crontab(hour=0, minute=0), daily_zephyr_ingest.s())
    sender.add_periodic_task(crontab(hour=0, minute=0), daily_sensor_community_ingest.s())
