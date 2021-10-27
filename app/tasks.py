import os

from celery import Celery

from api_wrappers.plume_wrapper import PlumeWrapper
from api_wrappers.zephyr_wrapper import ZephyrWrapper
from api_wrappers.base_wrapper import BaseSensor

app = Celery('tasks', broker=os.environ.get("CELERY_BROKER_URL"), backend=os.environ.get("CELERY_RESULT_BACKEND"))


def to_json(sensor: BaseSensor):
    return {"header": sensor.header, "rows": sensor.rows}


@app.task(name="get_plume_data")
def get_plume_data(start: float, end: float):
    try:
        pw = PlumeWrapper(os.environ.get("PLUME_EMAIL"), os.environ.get("PLUME_PASSWORD"), 85)
        return [to_json(s) for s in pw.get_sensors(start=start, end=end, sensors=pw.get_sensor_ids())]
    except IOError:
        return []


@app.task(name="get_zephyr_data")
def get_zephyr_data(start: float, end: float):
    try:
        z = ZephyrWrapper(os.environ.get("ZEPHYR_USERNAME"), os.environ.get("ZEPHYR_PASSWORD"))
        return [to_json(s) for s in z.get_sensors(start=start, end=end, slot="B", sensors=z.get_sensor_ids())]
    except IOError:
        return []


@app.task(name="get_sensor_community_data")
def get_sensor_community_data(start: float, end: float):
    return []
