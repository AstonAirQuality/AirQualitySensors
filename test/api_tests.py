import datetime as dt

import requests

endpoint = "http://0.0.0.0:8000"


def create_task(sensor):
    return requests.post(f"{endpoint}/api/tasks/create/{sensor}",
                         data={"start": dt.datetime(2021, 10, 1).timestamp(),
                               "end": dt.datetime(2021, 10, 10).timestamp()})


def get_task(task_id):
    return requests.get(f"{endpoint}/api/tasks/{task_id}")


if __name__ == '__main__':
    res = create_task("zephyr")
    print(res.text)
    # res = get_task("")
    # print(res.text)
