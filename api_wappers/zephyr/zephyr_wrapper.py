import datetime
import itertools
import json
from typing import Any, Iterator

import requests

from api_wappers.base_wrapper import BaseSensor, BaseWrapper


class ZephyrSensor(BaseSensor):
    """Per sensor object designed to wrap json objects returned by the Earth sense API."""

    def __init__(self, id_, header=(), row=()):
        super().__init__(id_, header, row)

    @staticmethod
    def from_json(id_, data: dict) -> Any:
        """Factory method builds ZephyrSensor objects from json dict returned by API

        :param id_: sensor id
        :param data: json dict
        :return: ZephyrSensor object
        """
        data.pop('UTS', None)
        zs = ZephyrSensor(id_, header=tuple(data.keys()))
        # Align any erroneous rows before appending to object
        for row in itertools.zip_longest(*[i["data"] for i in data.values()], fillvalue=None):
            zs.add_row(row)
        return zs


class ZephyrWrapper(BaseWrapper):
    """API wrapper for the Zephyr API."""

    def __init__(self, username: str, password: str):
        self.__username = username
        self.__pass = password

    def get_sensor_ids(self) -> Iterator[str]:
        """Fetches sensor ids from Earth sense API """
        try:
            json_ = (
                requests.get(f"https://data.earthsense.co.uk/zephyrsForUser/{self.__username}/{self.__pass}").json()[
                    'usersZephyrs'])
        except json.JSONDecodeError:
            return []
        for key in json_:
            yield json_[key]['zNumber']

    def get_sensors(self, sensors_ids: Iterator[str], start: datetime.datetime, end: datetime.datetime,
                    slot: str) -> Iterator[ZephyrSensor]:
        """Fetch json from API and return built Zephyr sensor objects.

        :param sensors_ids: id for senors to retrieve
        :param start: measurement start date
        :param end:  measurement end date
        :param slot: ???
        :return: ZephyrSensor objects
        """
        for id_ in sensors_ids:
            res = requests.get(f"https://data.earthsense.co.uk/dataForViewBySlots/"
                               f"{self.__username}"
                               f"/{self.__pass}"
                               f"/{id_}"
                               f"/{start.strftime('%Y%m%d%H%M')}"
                               f"/{end.strftime('%Y%m%d%H%M')}"
                               f"/{slot}/def/json/api")
            if res.ok:
                yield ZephyrSensor.from_json(id_, res.json()[f"slot{slot}"])


if __name__ == '__main__':
    # TODO: Make environment variables
    USERNAME = "AstonUniversity"
    PASSWORD = "Xo08R83d43e0Kk6"
    zw = ZephyrWrapper(USERNAME, PASSWORD)
    sensors = zw.get_sensors(zw.get_sensor_ids(),
                             start=datetime.datetime(2021, 9, 19),
                             end=datetime.datetime(2021, 9, 20),
                             slot="B")
    for s in sensors:
        print(s.id)
        print(s.dataframe)
