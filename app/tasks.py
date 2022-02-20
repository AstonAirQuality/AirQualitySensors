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
from influx import Influx

app = Celery('tasks', broker=os.environ.get("CELERY_BROKER_URL"), backend=os.environ.get("CELERY_RESULT_BACKEND"))


def to_json(sensor: BaseSensor):
    return {"header": sensor.header, "rows": sensor.rows}


def get_dates() -> Tuple[datetime, datetime]:
    """
    :return: start, end -> (now - 1 day), (now - 2 days)
    """
    return datetime.now() - timedelta(1), datetime.now() - timedelta(2)


# @app.on_after_configure.connect
# def setup_periodic_tasks(sender, **kwargs):
#     """
#     Daily tasks to retrieve sensor data.
#     """
#     sender.add_periodic_task(86400.0, write_plume_to_influx(name="plume_daily_task"))
#     sender.add_periodic_task(60.0, get_zephyr_data(*get_dates()), name="zephyr daily task")
#     sender.add_periodic_task(60.0, get_sensor_community_data(*get_dates()), name="sensor community daily task")


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
    print("sensor community task:", datetime.now())
    return []


@app.task(name="write_plume_data_to_db")
def write_plume_to_influx():
    pw = PlumeWrapper(os.environ.get("PLUME_EMAIL"), os.environ.get("PLUME_PASSWORD"), 85)
    sensors = pw.get_sensors(start=datetime.now() - timedelta(2),  # day before
                             end=datetime.now() - timedelta(1),  # yesterday
                             sensors=pw.get_sensor_ids(),
                             timeout=600)  # 10 minute time out
    ids = []
    for sensor in sensors:
        ids.append(sensor.id)
        Influx.write("plume", sensor)
    return ids


app.conf.beat_schedule = {
    # Executes plume task every day at mid night
    'every-day': {
        'task': 'tasks.write_plume_to_influx',
        'schedule': crontab(hour=0, minute=0),
        'args': (),
    },
}
