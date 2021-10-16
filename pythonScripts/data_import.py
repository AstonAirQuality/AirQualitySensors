import datetime
import json
import time
from typing import List, Dict
from tempfile import SpooledTemporaryFile

import requests


class PlumeSensor:
    pass


class PlumeExtract:
    def __init__(self, file: SpooledTemporaryFile):
        self.file = file
        self.sensors = []


class PlumeDownload:
    # TODO: Make environment variables
    EMAIL = "180086320@aston.ac.uk"
    PASSWORD = "aston1234"
    PLUME_FIREBASE_API_KEY = "AIzaSyA77TeuuxEwGLR3CJV2aQxLYIetMqou5No"

    def __init__(self):
        self.session = self.__login()

    def __login(self) -> requests.Session:
        session = requests.Session()
        res = requests.post(
            f"https://www.googleapis.com/identitytoolkit/v3/relyingparty/verifyPassword?"
            f"key={self.PLUME_FIREBASE_API_KEY}", data={"email": self.EMAIL,
                                                        "password": self.PASSWORD,
                                                        "returnSecureToken": True})
        if res.status_code != 200:
            raise IOError()

        json_ = json.loads(res.content)
        auth_token = json_["idToken"]
        auth_key = json_["localId"]
        json_ = json.loads(session.post("https://api-preprod.plumelabs.com/2.0/user/token",
                                        data={"auth_type": "FIREBASE",
                                              "auth_key": auth_key,
                                              "auth_token": auth_token,
                                              "auth_secret": ""}).content)
        bearer = json_["token"]

        # add bearer to session header
        session.headers["authorization"] = f"Bearer {bearer}"
        return session

    def get_api_side_task_queue(self) -> Dict:
        return json.loads(
            self.session.get("https://api-preprod.plumelabs.com/2.0/user/organizations/85").content)["export_tasks"]

    def get_sensor_ids(self) -> List[str]:
        try:
            json_ = (
                json.loads(
                    self.session.get("https://api-preprod.plumelabs.com/2.0/user/organizations/85/sensors").content))
        except json.JSONDecodeError:
            return []
        return [sensor["id"] for sensor in json_["sensors"]]

    def get_zip_file_link(self, sensors: List[str], start: datetime.datetime, end: datetime.datetime,
                          timeout=15) -> str:
        task_id = json.loads(
            self.session.post("https://api-preprod.plumelabs.com/2.0/user/organizations/85/sensors/export",
                              json={
                                  "sensors": sensors,
                                  "end_date": int(end.timestamp()),
                                  "start_date": int(start.timestamp()),
                                  "gps": False,
                                  "kml": False,
                                  "id": "85",
                                  "no2": True,
                                  "pm1": True,
                                  "pm10": True,
                                  "pm25": True,
                                  "voc": True
                              }).content)["id"]
        link = None
        for _ in range(timeout):
            # wait for Plume API to create zip
            link = json.loads(
                self.session.get(f"https://api-preprod.plumelabs.com/2.0/user/export-tasks/{task_id}").content)["link"]
            if link:
                break
            time.sleep(1)
        return link

    def download(self):
        pass


if __name__ == '__main__':
    pi = PlumeDownload()
    print(pi.get_zip_file_link(pi.get_sensor_ids(),
                               start=datetime.datetime(2021, 9, 30),
                               end=datetime.datetime(2021, 10, 13)))
