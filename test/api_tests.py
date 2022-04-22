import datetime as dt

import requests

local_test_endpoint = "http://0.0.0.0:8000"


def create_task(sensor):
    return requests.post(f"{local_test_endpoint}/api/tasks/create/{sensor}",
                         data={"start": dt.datetime(2021, 1, 1).timestamp(),
                               "end": dt.datetime(2021, 6, 1).timestamp()})


def get_task(task_id):
    res = requests.get(f"{local_test_endpoint}/api/tasks/{task_id}")
    print(res.text)


if __name__ == '__main__':
    # res = create_task("plume")
    # print(res.text)
    get_task("0aa9e596-15bc-4c21-86dc-8d006110563b")
