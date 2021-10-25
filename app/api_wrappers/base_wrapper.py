import abc
from typing import Iterable

import pandas as pd


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
    def get_sensors(self, *args, **kwargs):
        ...
