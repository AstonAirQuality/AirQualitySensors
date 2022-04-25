import time

from locust import HttpUser, task, between
import random


class WebUser(HttpUser):
    wait_time = between(1, 2)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.sensors = ["plume", "zephyr", "sensor_community"]

    def on_start(self):
        ...

    @task
    def test_task(self):
        """
        Randomly pick a sensor and time range between 01/2020 - 01/2022, submit task to server, check every send for
        task status, upon SUCCESS return, else time out after 20 seconds and move onto another request.
        """
        lower = 1640995200  # 01/2022
        upper = 1577836800  # 01/2021
        start = random.Random().randint(upper, lower)
        end = random.Random().randint(start, lower)  # end has to after start
        sensor = random.Random().choice(self.sensors)
        ret = self.client.post("/api/tasks/create/" + sensor, data={"start": start, "end": end})
        task_id = ret.json()["task_id"]
        for _ in range(20):
            time.sleep(1)
            ret = self.client.get("/api/tasks/" + task_id)
            if ret.json()["task_status"] == "SUCCESS":
                return
