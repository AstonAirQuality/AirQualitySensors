import abc
import functools
from collections import namedtuple
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


class BaseSensorIterator:
    Row = namedtuple("Row", "timestamp fields tags")

    def __init__(self, id_, header, rows):
        self.sensor_id = id_
        self.header = header
        self.rows = rows
        self._index = 0

    @abc.abstractmethod
    def __next__(self):
        """
        :return: namedtuple(timestamp=timestamp, fields={...}, tags={...})
        """
        ...


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
        final_row = []
        for entry in row:
            i = str(entry)
            if i.isdigit():
                final_row.append(int(i))
            else:
                try:
                    final_row.append(float(i))
                except ValueError:
                    # append to original entry type
                    final_row.append(entry)
        self.rows.append(final_row)

    @property
    def dataframe(self) -> pd.DataFrame:
        """Writes headers and rows into a DataFrame.
        """
        return pd.DataFrame(self.rows, columns=self.header)

    @abc.abstractmethod
    def __iter__(self):
        ...


class BaseWrapper(abc.ABC):

    @abc.abstractmethod
    def get_sensor_ids(self, *args, **kwargs) -> Iterable[str]:
        ...

    @abc.abstractmethod
    def get_sensors(self, start: Union[dt.datetime, float, int], end: [dt.datetime, float, int], *args, **kwargs):
        ...
