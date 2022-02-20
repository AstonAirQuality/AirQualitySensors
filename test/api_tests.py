import datetime as dt

import requests

local_test_endpoint = "http://0.0.0.0:8000"
remote_test_endpoint = "http://192.168.1.30:8000"


def update_db():
    res = requests.post(f"{remote_test_endpoint}/api/tasks/database/update")
    print(res.text)


def create_task(sensor):
    return requests.post(f"{remote_test_endpoint}/api/tasks/create/{sensor}",
                         data={"start": dt.datetime(2022, 1, 1).timestamp(),
                               "end": dt.datetime(2022, 1, 31).timestamp()})


def get_task(task_id):
    res = requests.get(f"{remote_test_endpoint}/api/tasks/{task_id}")
    print(res.text)


if __name__ == '__main__':
    update_db()
    # # res = create_task("plume")
    # # print(res.text)
    # get_task("72923c0b-9a1e-4bb4-84f4-29ac48424be8")
