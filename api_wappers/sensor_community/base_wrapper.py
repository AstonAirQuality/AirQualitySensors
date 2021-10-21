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
        """Append row to internal rows list
        """
        self.rows.append(row)

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
