import csv
import datetime as dt
import json
import pathlib
import time
import io
from typing import Dict, Any, Iterable, Iterator, Union

import zipfile
import requests
import s2sphere

from .base_wrapper import BaseWrapper, BaseSensor, correct_timestamp, BaseSensorIterator


class APITimeoutException(IOError):
    pass


class PlumeSensorIterator(BaseSensorIterator):

    def __init__(self, sensor_id, header, rows):
        super().__init__(sensor_id, header, rows)
        self.correct_long_lat()

    def correct_long_lat(self):
        """latitude and longitude are added to the objects header if they are not already contained. Row lengths are
        subsequently corrected with empty floats.
        """
        for direction in ["latitude", "longitude"]:
            if direction not in self.header:
                self.header.append(direction)
                for row in self.rows:
                    row.append(0.0)
        for row in self.rows:
            # round long and latitude to 4 decimal palaces (11.1m) to reduce series cardinality and keep db performant.
            # http://wiki.gis.com/wiki/index.php/Decimal_degrees
            row[-1] = round(row[-1], 5)
            row[-2] = round(row[-2], 5)

    def get_s2_cell_token(self, long, lat):
        """
        The Geo package uses the S2 Geometry Library to represent geographic coordinates on a three-dimensional sphere.
        The sphere is divided into cells, each with a unique 64-bit identifier (S2 cell ID).
        Grid and S2 cell ID accuracy are defined by a level.

        https://docs.influxdata.com/influxdb/cloud/query-data/flux/geo/shape-geo-data/#generate-s2-cell-id-tokens-language-specific-libraries
        """
        return s2sphere.CellId.from_lat_lng(s2sphere.LatLng(long, lat)).to_token()

    def __next__(self):
        """
        Implements the BaseSensorIterator API

        sensor_id, s2_cell_id are indexed by the database as tags.
        remaining measurements, latitude and longitude are stored in non-indexed fields.

        """
        if self._index >= len(self.rows):
            self._index = 0
            raise StopIteration()
        row = self.rows[self._index]
        fields = dict(zip(self.header[2:], row[2:]))
        ret = self.Row(row[0], fields, {"sensor_id": self.id, "s2_cell_id": self.get_s2_cell_token(row[-1], row[-2])})
        self._index += 1
        return ret


class PlumeSensor(BaseSensor):
    """Per sensor object designed to wrap the csv files returned by the Plume API.

    Example Usage:
        ps = PlumeSensor.from_csv("16397", open("sensor_measures_20211004_20211008_1.csv"))
        print(ps.DataFrame)

    Headers:
        timestamp,"date (UTC)","NO2 (ppb)","VOC (ppb)","pm 10 (ug/m3)","pm 2.5 (ug/m3)","NO2 (Plume AQI)","VOC (Plume AQI)","pm 10 (Plume AQI)","pm 2.5 (Plume AQI)","latitude","logitude"

    """

    def __init__(self, sensor_id, header=(), rows=()):
        super().__init__(int(sensor_id), header, rows)

    def add_row(self, row: list):
        """Standardise types to ints and floats to avoid type conflicts at the database level

        Convert first element (timestamp) to int, keep second element type, change all other elements to floats

        TODO: Standardise and clean up to account for potential changes to the plume API.
        """
        self.rows.append([int(row[0]), row[1], *[float(i) if i else 0.0 for i in row[2:]]])

    @property
    def pollutants(self):
        """Returns pollutants found in the header.
        """
        return self.header[2:]

    @staticmethod
    def from_csv(sensor_id: str, csv_file: io.StringIO) -> Any:
        """Factory method builds PlumeSensor from file like object
        containing csv data.

        :param sensor_id: id number of sensor
        :param csv_file: csv file like object
        :return:
        """
        reader = csv.reader(csv_file, dialect=csv.unix_dialect)
        header = next(reader)
        sensor = PlumeSensor(sensor_id, header, [])
        for row in reader:
            sensor.add_row(row)
        return sensor

    def __iter__(self):
        return PlumeSensorIterator(self.id, self.header, self.rows)


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

    def get_zip_file_link(self, sensors: Iterable[str], start: dt.datetime, end: dt.datetime,
                          timeout) -> str:
        task_id = self.__session.post(f"https://api-preprod.plumelabs.com/2.0/user/organizations/"
                                      f"{self.org}/sensors/export",
                                      json={
                                          "sensors": sensors,
                                          "end_date": int(end.timestamp()),
                                          "start_date": int(start.timestamp()),
                                          "gps": True,
                                          "kml": False,
                                          "merged": True,
                                          "id": self.org,
                                          "no2": True,
                                          "pm1": True,
                                          "pm10": True,
                                          "pm25": True,
                                          "voc": True
                                      }).json()["id"]
        for _ in range(timeout):
            # wait for Plume API to create zip
            link = self.__session.get(f"https://api-preprod.plumelabs.com/2.0/user/export-tasks/{task_id}").json()[
                "link"]
            if link:
                break
            time.sleep(1)
        else:
            raise APITimeoutException("Plume API timed out when attempting to retrieve zip file link")
        return link

    def extract_zip(self, link):
        """Download and extract zip into memory.

        :param link: url to sensor data zip file
        :return:sensor id, sensor data in a string buffer
        """
        res = requests.get(link, stream=True)
        if not res.ok:
            raise IOError(f"Failed to download zip file from link: {link}")
        if not len(res.content):
            # return an empty iterator if zip file is empty
            return ()
        zip_ = zipfile.ZipFile(io.BytesIO(res.content))
        for name in zip_.namelist():
            path_parts = pathlib.PurePath(name).parts
            # extract only location merged sensor data
            if path_parts[3] == "sensor_merged_1.csv":
                # split path and strip string to extract sensor id
                yield path_parts[2].lstrip("sensor_"), io.StringIO(zip_.read(name).decode())

    @correct_timestamp
    def get_sensors(self, start: Union[dt.datetime, float, int], end: [dt.datetime, float, int],
                    sensors: Iterable[str], timeout=30) -> Iterator[PlumeSensor]:
        """Downloads the sensor data from the Plume API and loads to PlumeSensor objects.

        :param timeout: wait this many seconds before timing out request to plume api
        :param sensors: sensors to retrieve
        :param start: start time
        :param end: end time
        :return: Generator of PlumeSensor Objects for each sensor populated with data from the API
        """
        for sensor, buffer in self.extract_zip(self.get_zip_file_link(sensors, start, end, timeout)):
            yield PlumeSensor.from_csv(sensor, buffer)
