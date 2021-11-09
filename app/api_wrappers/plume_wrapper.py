import csv
import datetime as dt
import json
import pathlib
import time
import io
from typing import List,Dict, Any, Iterable, Iterator, Union

import zipfile

import requests

from .base_wrapper import BaseWrapper, BaseSensor, correct_timestamp


class APITimeoutException(IOError):
    pass


class PlumeSensor(BaseSensor):
    """Per sensor object designed to wrap the dictionary formatted data returned by the Plume API.

    Example Usage:
        ps = PlumeSensor.from_csv("16397", [ {'id':11242, 'date': 163365002, 'no2': 0.0021, 'voc': 4.122415, 'pm1': 2.41 ,'pm25': 4.21,'pm10':67.215} ])
        print(ps.DataFrame)
    """

    def __init__(self, id_, header=(), rows=()):
        super().__init__(id_, header, rows)

    @property
    def pollutants(self):
        """Returns pollutants found in the header.
        """
        return self.header[2:]

    @staticmethod
    def from_dict(sensor_id: str, dictionaries: List) -> Any:
        """Factory method builds PlumeSensor from file like object
        containing data in a dictionary format.

        :param sensor_id: id number of sensor
        :param dictionaries: list of dictionaries which contain the sensor data
        :return:
        """
        header = list(dictionaries[0].keys())[1::]
        rows = [list(row.values())[1::] for row in dictionaries]
        sensor = PlumeSensor(sensor_id, header, rows)
    
        return sensor


class PlumeWrapper(BaseWrapper):
    """API wrapper for the Plume dashboard.
    """
    PLUME_FIREBASE_API_KEY = "AIzaSyA77TeuuxEwGLR3CJV2aQxLYIetMqou5No"

    def __init__(self, email: str, password: str, org_number: int):
        self.org = str(org_number)
        self.__session = self.__login(email, password)

    def __login(self, email, password) -> requests.Session:
        """Logs into the Plume API

        The API uses Google Firebase for auth, each subsequent request to the API after login must
        be made with the "Bearer" auth token for the API to respond.

        :param email: login email
        :param password: login password
        :return: Logged in session
        """
        session = requests.Session()
        res = requests.post(
            f"https://www.googleapis.com/identitytoolkit/v3/relyingparty/verifyPassword?"
            f"key={self.PLUME_FIREBASE_API_KEY}", data={"email": email,
                                                        "password": password,
                                                        "returnSecureToken": True})
        if not res.ok:
            raise IOError("Login failed")
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
        return self.__session.get(
            f"https://api-preprod.plumelabs.com/2.0/user/organizations/{self.org}").json()["export_tasks"]

    def get_sensor_ids(self) -> Iterable[str]:
        try:
            json_ = self.__session.get(
                f"https://api-preprod.plumelabs.com/2.0/user/organizations/{self.org}/sensors").json()
        except json.JSONDecodeError:
            return []
        return [sensor["id"] for sensor in json_["sensors"]]
        
    @correct_timestamp
    def get_sensors(self, start: Union[dt.datetime, float, int], end: Union[dt.datetime, float, int],
                    sensors: Iterable[str]) -> Iterator[PlumeSensor]:
        """Downloads the sensor data from the Plume API and loads to PlumeSensor objects.

        :param sensors: sensors to retrieve
        :param start: start time
        :param end: end time
        :return: Iterator of PlumeSensor Objects for each sensor populated with data from the API
        """
        for sensorId in sensors:
            res = self.__session.get(f"https://api-preprod.plumelabs.com/2.0/user/organizations/85/sensors/{sensorId}/measures?start_date={int(start.timestamp())}&end_date={int(end.timestamp())}&offset=0",
                        data={"start_date": start, "end_date": end,"offset": 0})
            yield PlumeSensor.from_dict(sensorId, res.json()['measures'])
            break #TODO remove

    # def get_zip_file_link(self, sensors: Iterable[str], start: dt.datetime, end: dt.datetime,
    #                       timeout=15) -> str:
    #     task_id = self.__session.post(f"https://api-preprod.plumelabs.com/2.0/user/organizations/"
    #                                   f"{self.org}/sensors/export",
    #                                   json={
    #                                       "sensors": sensors,
    #                                       "end_date": int(end.timestamp()),
    #                                       "start_date": int(start.timestamp()),
    #                                       "gps": False,
    #                                       "kml": False,
    #                                       "id": self.org,
    #                                       "no2": True,
    #                                       "pm1": True,
    #                                       "pm10": True,
    #                                       "pm25": True,
    #                                       "voc": True
    #                                   }).json()["id"]
    #     for _ in range(timeout):
    #         # wait for Plume API to create zip
    #         link = self.__session.get(f"https://api-preprod.plumelabs.com/2.0/user/export-tasks/{task_id}").json()[
    #             "link"]
    #         if link:
    #             break
    #         time.sleep(1)
    #     else:
    #         raise APITimeoutException("Plume API timed out when attempting to retrieve zip file link")
    #     return link

    # def extract_zip(self, link):
    #     """Download and extract zip into memory.

    #     :param link: url to sensor data zip file
    #     :return:sensor id, sensor data in a string buffer
    #     """
    #     res = requests.get(link, stream=True)
    #     if not res.ok:
    #         raise IOError(f"Failed to download zip file from link: {link}")
    #     zip_ = zipfile.ZipFile(io.BytesIO(res.content))
    #     for name in zip_.namelist():
    #         # split path and strip string to extract sensor id
    #         yield pathlib.PurePath(name).parts[2].lstrip("sensor_"), io.StringIO(zip_.read(name).decode())