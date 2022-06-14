import datetime as dt
import sys
import time

import pandas
import requests

local_test_endpoint = "http://0.0.0.0:8000"


def create_task(sensor):
    return requests.post(f"{local_test_endpoint}/api/tasks/create/{sensor}",
                         data={"start": dt.datetime(2021, 1, 1).timestamp(),
                               "end": dt.datetime(2022, 1, 1).timestamp()})


def get_task(task_id):
    return requests.get(f"{local_test_endpoint}/api/tasks/{task_id}").json()


def to_df(json_):
    result = json_["task_result"]
    for sensor in result:
        yield sensor["sensor_id"], pandas.DataFrame(sensor["rows"], columns=sensor["header"])


def check_status(json_):
    return json_["task_status"]


def test(bucket):
    print("Testing Bucket:", bucket)
    task_id = create_task(bucket).json()["task_id"]

    print("Task ID:", task_id)
    print("Checking task for next 20 second")

    for _ in range(20):
        time.sleep(1)
        task = get_task(task_id)

        status = check_status(task)
        print("Task Status:", status)
        if status == "SUCCESS":
            for id_, df in to_df(task):
                print("Sensor ID:", id_)
                print(df)
            return
    print("Timeout", file=sys.stderr)


if __name__ == '__main__':
    """
    Retrieve all data available for each bucket between 2021 - 2022
    """
    test("plume")
    test("zephyr")
    test("sensor_community")
