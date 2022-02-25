"""
TODO: Implement Readable and Writable classes
"""
import datetime as dt
import itertools
import json
from typing import Any, Iterator, Union

import requests

from .base_wrapper import BaseSensor, BaseWrapper, correct_timestamp


class ZephyrSensor(BaseSensor):
    """Per sensor object designed to wrap json objects returned by the Earth sense API."""

    def __init__(self, id_, header=(), rows=()):
        super().__init__(id_, header, rows)

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

    def get_writable(self):
        pass


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

    @correct_timestamp
    def get_sensors(self, start: Union[dt.datetime, float, int], end: Union[dt.datetime, float, int],
                    slot: str, sensors: Iterator[str]) -> Iterator[ZephyrSensor]:
        """Fetch json from API and return built Zephyr sensor objects.

        :param sensors: id for senors to retrieve
        :param start: measurement start date
        :param end:  measurement end date
        :param slot: ???
        :return: ZephyrSensor objects
        """
        for id_ in sensors:
            res = requests.get(f"https://data.earthsense.co.uk/dataForViewBySlots/"
                               f"{self.__username}"
                               f"/{self.__pass}"
                               f"/{id_}"
                               f"/{start.strftime('%Y%m%d%H%M')}"
                               f"/{end.strftime('%Y%m%d%H%M')}"
                               f"/{slot}/def/json/api")
            if res.ok:
                yield ZephyrSensor.from_json(id_, res.json()[f"slot{slot}"])
