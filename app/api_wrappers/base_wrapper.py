import abc
import functools
from typing import Iterable, Union

import datetime as dt

import pandas as pd


def correct_timestamp(func):
    """
    decorator converts start and end timestamps to datetime objects
    """

    @functools.wraps(func)
    def stub(self, start, end, *args, **kwargs):
        if type(start) in (int, float):
            start = dt.datetime.fromtimestamp(start)
        if type(end) in (int, float):
            end = dt.datetime.fromtimestamp(end)
        return func(self, start, end, *args, **kwargs)

    return stub


class BaseSensor:
    """
    Base class for sensor objects
    """

    def __init__(self, id_, header, row):
        self.id = id_
        self.header = header
        self.rows = list(row)

    def add_row(self, row: Iterable):
        """Normalise and append row to internal list.

        Coverts all digits to int objects, all elements are initially converted to strings before
        digit check to avoid type errors.

        :param row: row to add to plume sensor
        """
        self.rows.append([int(i) if str(i).isdigit() else i for i in row])

    @property
    def dataframe(self) -> pd.DataFrame:
        """Writes headers and rows into a DataFrame.
        """
        return pd.DataFrame(self.rows, columns=self.header)


class BaseWrapper(abc.ABC):

    @abc.abstractmethod
    def get_sensor_ids(self, *args, **kwargs) -> Iterable[str]:
        ...

    @abc.abstractmethod
    def get_sensors(self, start: Union[dt.datetime, float, int], end: [dt.datetime, float, int], *args, **kwargs):
        ...
