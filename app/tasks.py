import datetime
import os

from celery import Celery
from api_wrappers.plume_wrapper import PlumeWrapper
from api_wrappers.zephyr_wrapper import ZephyrWrapper
from api_wrappers.base_wrapper import BaseSensor

app = Celery('tasks', broker=os.environ.get("CELERY_BROKER_URL"), backend=os.environ.get("CELERY_RESULT_BACKEND"))


def to_json(sensor: BaseSensor):
    return {"header": sensor.header, "rows": sensor.rows}


@app.task
def get_plume_data(start: datetime.datetime, end: datetime.datetime):
    try:
        pw = PlumeWrapper(os.environ.get("PLUME_EMAIL"), os.environ.get("PLUME_PASSWORD"), 85)
        return [to_json(s) for s in pw.get_sensors(pw.get_sensor_ids(), start, end)]
    except IOError:
        return []


@app.task
def get_zephyr_data(start: datetime.datetime, end: datetime.datetime):
    try:
        z = ZephyrWrapper(os.environ.get("ZEPHYR_USERNAME"), os.environ.get("ZEPHYR_PASSWORD"))
        return [to_json(s) for s in z.get_sensors(z.get_sensor_ids(), start, end, "B")]
    except IOError:
        return []


@app.task
def get_sensor_community_data(start: datetime.datetime, end: datetime.datetime):
    return []
