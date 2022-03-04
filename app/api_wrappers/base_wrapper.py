import abc
import functools
from collections import namedtuple
from typing import Iterable, Union

import datetime as dt

import pandas as pd
import s2sphere


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


class BaseSensorReadable:
    """Returned by the influxdb reader
    """

    def __init__(self, id_, header, rows):
        self.id = id_
        self.header = header
        self.rows = list(rows)

    def __repr__(self):
        return f"{self.id} | Headers {self.header} | Row count: {len(self.rows)}"


class BaseSensorWritable:
    """Creates an influxdb compatible named tuple for each row in the sensor object
    """
    Row = namedtuple("Row", "timestamp fields tags")

    def __init__(self, id_, header, rows):
        self.id = id_
        self.header = header
        self.rows = rows

    @abc.abstractmethod
    def __iter__(self):
        """
        :yield: namedtuple(timestamp=timestamp, fields={...}, tags={...})
        """
        ...

    def round_long_lat_in_fields(self, fields: dict, accuracy: int = 5) -> dict:
        """rounds lat and lon in fields before committing to the database.

        To be called after self.correct_long_lat_in_header

        TODO: round to 5 decimal places.
        round long and latitude to 4 decimal palaces (11.1m) to reduce series cardinality and keep db performant.
        http://wiki.gis.com/wiki/index.php/Decimal_degrees
        """
        for direction in ["lat", "lon"]:
            if fields[direction] is not None:
                fields[direction] = round(fields[direction], accuracy)
            else:
                fields[direction] = 0.0  # if lat or lon is None, change to 0.0 to keep db from crashing on geo reads
        return fields

    def correct_long_lat_in_header(self):
        """latitude and longitude are added to the objects' header if they are not already contained. Row lengths are
        subsequently corrected with empty floats.
        """
        for direction in ["latitude", "longitude"]:
            if direction not in self.header:
                # shorten to lat, lon
                self.header.append(direction[:3])
                for row in self.rows:
                    row.append(0.0)
            else:
                # replace with lat, lon
                self.header = [i.replace(direction, direction[:3]) for i in self.header]

    def get_s2_cell_token(self, lon: int, lat: int):
        """
        The Geo package uses the S2 Geometry Library to represent geographic coordinates on a three-dimensional sphere.
        The sphere is divided into cells, each with a unique 64-bit identifier (S2 cell ID).
        Grid and S2 cell ID accuracy are defined by a level.

        https://docs.influxdata.com/influxdb/cloud/query-data/flux/geo/shape-geo-data/#generate-s2-cell-id-tokens-language-specific-libraries
        """
        return s2sphere.CellId.from_lat_lng(s2sphere.LatLng(lon, lat)).to_token()


class BaseSensor:
    """
    Base class for sensor objects
    """

    def __init__(self, id_, header, rows):
        self.id = id_
        self.header = header
        self.rows = list(rows)

    def add_row(self, row: Iterable):
        """Normalise and append row to internal list.

        Coverts all digits to int objects, all elements are initially converted to strings before
        digit check to avoid type errors.

        :param row: row to add to plume sensor
        """
        self.rows.append(row)

    @property
    def dataframe(self) -> pd.DataFrame:
        """Writes headers and rows into a DataFrame.
        """
        return pd.DataFrame(self.rows, columns=self.header)

    @abc.abstractmethod
    def get_writable(self):
        ...

    def __repr__(self):
        return f"{self.id} | Headers {self.header} | Row count: {len(self.rows)}"


class BaseWrapper(abc.ABC):

    @abc.abstractmethod
    def get_sensor_ids(self, *args, **kwargs) -> Iterable[str]:
        ...

    @abc.abstractmethod
    def get_sensors(self, start: Union[dt.datetime, float, int], end: [dt.datetime, float, int], *args, **kwargs):
        ...
