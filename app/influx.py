import functools
import itertools
import os
import datetime as dt
import sys
import timeit
from collections import defaultdict
from typing import Iterator

from influxdb_client import InfluxDBClient, WriteOptions, Point, Dialect

# TODO: add . to front of imports when running tests
from api_wrappers.base_wrapper import BaseSensorWritable, BaseSensorReadable
from api_wrappers.plume_wrapper import PlumeSensorReadable
from api_wrappers.sensor_community_wrapper import SCSensorReadable
from api_wrappers.zephyr_wrapper import ZephyrSensorReadable

BUCKET_MAPPINGS = {"plume": PlumeSensorReadable, "zephyr": ZephyrSensorReadable, "sensor_community": SCSensorReadable}


def check_conflicts(func):
    @functools.wraps(func)
    def stub(self, *args, **kwargs):
        # checks if function has active conflicts if so ignore call
        for i in self._conflicts[func.__name__]:
            if self._function_chain[i] is not None:
                return self
        return func(self, *args, **kwargs)

    return stub


class InfluxQueryBuilder:
    """Builds custom Flux queries by chaining python functions.
    Maintains query structure and logical function (required by flux) order regardless of
    call order. e.g .filter().range() is converted to .range().filter() as range comes before
    filter in the flux language.
    """

    def __init__(self, bucket):
        self.geo_temporal_query = False
        self.bucket = bucket
        self._conflicts = {"radius": ["polygon"],
                           "polygon": ["radius"]}  # maintains an index of what functions conflict with each other
        self._function_chain = {"range": None, "filters": None, "radius": None, "polygon": None}
        self.__fields = []

    @check_conflicts
    def polygon(self, points: list):
        str_ = f"geo.toRows()\n" \
               f"|> geo.strictFilter(" \
               f"\n\tregion: {{" \
               f"\n\tpoints: ["
        for point in points:
            str_ += f"\n\t\t{{lat: {point[0]}, lon: {point[1]}}},"
        str_ = str_.rstrip(",")
        str_ += f"\n\t]}})"
        self._function_chain["radius"] = str_
        self.geo_temporal_query = True
        return self

    @check_conflicts
    def radius(self, lat, lon, radius):
        self._function_chain["radius"] = f"geo.toRows()\n" \
                                         f"|> geo.strictFilter(" \
                                         f"\n\tregion: {{" \
                                         f"\n\t\tlat: {lat}," \
                                         f"\n\t\tlon: {lon}," \
                                         f"\n\t\tradius: {radius}" \
                                         f"\n\t}})"
        self.geo_temporal_query = True
        return self

    def range(self, start="0", stop=None):
        if stop is None:
            self._function_chain["range"] = f"range(start: {int(start)})"
        else:
            self._function_chain["range"] = f"range(start: {int(start)}, stop: {int(stop)})"
        return self

    def filter(self, expression, param_name="r"):
        """Will keep appending filter functions on each call.
        Args:
            expression: flux filter expression
            param_name: name of param in flux filter expression
        Returns:
            Instance of self
        """
        query_string = f"filter(fn: ({param_name}) => {expression})"
        if self._function_chain["filters"] is None:
            self._function_chain["filters"] = [query_string]
        else:
            self._function_chain["filters"].append(query_string)
        return self

    def field(self, field):
        """Appends field to function chain.
        Returns:
            Instance of self
        """
        self.__fields.append(f'r["_field"] == "{field}"')
        return self

    def measurement(self, measurement):
        """Call measurement before field
        Returns:
            Instance of self
        """
        self.filter(f'r["_measurement"] == "{measurement}"')
        return self

    def build(self):
        """Build the flux query from the function chain.
        Returns:
            Built Flux query string.
        """
        if self.__fields:
            self.filter(" or ".join(self.__fields))
        query = f"import \"experimental/geo\"\n\nfrom(bucket: \"{self.bucket}\")"
        for k, v in self._function_chain.items():
            if v is not None:
                if type(v) is list:
                    for item in v:
                        query += f"\n|> {item}"
                else:
                    query += f"\n|> {v}"
        return query


class Table:
    """
    Builds and corrects data to allow for easy insertion into a dataframe. Assumes all data inserted must be of the
    measurement.
        Typical usage example:
        table = Table()
        table.insert("2020-01-23 12:49:09", "s1", "a1", 0.07695700000000001, 1)
        table.insert("2020-01-23 12:49:29", "s2", "a2", 0.039731, 2)
        ....
        t = table.build()
    """

    def __init__(self):
        self.measurement = None
        self.fields = set()
        self.index = defaultdict(list)  # {"timestamp": [field0, field1, fieldN, ...]}
        self.data = defaultdict(list)  # {"timestamp": [{"measurement": "AMU", "field": "mean", "value": "01"}, ...]}
        self.corrected = False

    def insert(self, timestamp: str, measurement: str, field: str, value: float):
        """
        Insert entry into table. The entry is inserted into the internal index and data structure.
        If the table has already been built all subsequent inserts are ignored.
        """
        if self.corrected:
            return
        if self.measurement is None:
            self.measurement = measurement
        self.data[timestamp].append({"field": field, "value": value})
        self.index[timestamp].append(field)
        self.fields.add(field)

    def __correct(self):
        """Pads out internal data structure.
        Compares fields and times stamps, if there are fields that don't have values at specific time stamps into the
        table a None value is inserted in this position to ensure all columns have the same length.
        Function can only be called once.
        """
        if self.corrected:
            return
        self.corrected = True
        for k, v in self.index.items():
            missing_fields = list(self.fields - set(v))
            if len(missing_fields) > 0:
                for field in missing_fields:
                    self.data[k].append({"field": field, "value": None})

    def build(self):
        """Builds final table like data structure.
        Returns:
            A dict with the tabular structure:
            {"timestamp": [time0, time1, timeN, ...],
            "asset": [a, a, a, ...],
            "field0": [v0, v1, vN, ...],
            "field1": [v0, v1, vN, ...],
            "fieldN": [v0, v1, vN, ...],
            ...}
        """
        self.__correct()
        base = defaultdict(list)
        for k, v in self.data.items():
            # base["timestamp"].append(pandas.to_datetime(k))
            base["timestamp"].append(k)
            base["measurement"].append(self.measurement)
            for i in v:
                base[i["field"]].append(i["value"])
        return dict(base)


class Influx:

    @staticmethod
    def get_client(url=os.getenv("INFLUXDB_V2_URL"), org=os.getenv("INFLUXDB_V2_ORG"),
                   token=os.getenv("INFLUXDB_V2_TOKEN")):
        return InfluxDBClient(url=url, org=org, token=token)

    @staticmethod
    def write(bucket: str, writable: BaseSensorWritable, measurement="air_quality", client=None):
        # select static client if no client is specified by the user, helps with testability
        writer = (Influx.get_client() if client is None else client).write_api(
            write_options=WriteOptions(batch_size=50_000, flush_interval=10_000))
        for entry in writable:
            # TODO: Find out why Influx does not insert correctly with UNIX timestamp
            record_ = Point(measurement).time(dt.datetime.fromtimestamp(entry.timestamp))
            # add fields to record
            for k, v in entry.fields.items():
                record_.field(k, v)
            # add tags to record
            for k, v in entry.tags.items():
                record_.tag(k, v)
            writer.write(bucket=bucket, record=record_)
        # flush contents of writer to database
        writer.close()

    @staticmethod
    def __geo_temporal_read(query: InfluxQueryBuilder, reader) -> Iterator[BaseSensorReadable]:
        """Geo temporal data is returned differently than standard reads and is processed accordingly.
        """
        start = timeit.default_timer()
        csv_buffer = list(reader.query_csv(query.build(), dialect=Dialect()))
        end = timeit.default_timer()
        aggregator = defaultdict(list)
        print(f"DB READ TIME {end - start}s")
        header = csv_buffer[0]
        for line in itertools.islice(csv_buffer, 1, None):
            dict_ = dict(zip(header, line))
            try:
                sensor_id = int(dict_["sensor_id"])
            except KeyError:
                continue
            aggregator[sensor_id].append(list(dict_.values()))
        for sensor_id, v in aggregator.items():
            sen = BUCKET_MAPPINGS[query.bucket](sensor_id, header, v)
            yield sen

    @staticmethod
    def read(query: InfluxQueryBuilder, client=None) -> Iterator[BaseSensorReadable]:
        """Send query to db through client and return tabulated output
        Args:
            query: FluxQL query to send to database
            client: Influx python client
        Returns:
            Table containing data

        TODO: remove debug timer
        """
        # select static client if no client is specified by the user, helps with testability
        reader = (Influx.get_client() if client is None else client).query_api()
        if query.geo_temporal_query:
            yield from Influx.__geo_temporal_read(query, reader)
            return

        start = timeit.default_timer()
        csv_buffer = list(reader.query_csv(query.build(), dialect=Dialect()))
        end = timeit.default_timer()
        print(f"DB READ TIME {end - start}s")
        if len(csv_buffer) < 3:
            return []
        headers = csv_buffer[0]
        aggregator = defaultdict(list)
        for line in itertools.islice(csv_buffer, 1, None):
            if line in (headers, []):
                continue
            dict_ = dict(zip(headers, line))
            try:
                sensor_id = int(dict_["sensor_id"])
            except KeyError:
                continue
            except ValueError:
                sensor_id = dict_["sensor_id"]
            try:
                aggregator[sensor_id].append([dict_["_time"], dict_["_measurement"], dict_["_field"],
                                              float(dict_["_value"])])
            except ValueError:
                aggregator[sensor_id].append([dict_["_time"], dict_["_measurement"], dict_["_field"],
                                              dict_["_value"]])
            except KeyError:
                print(dict_, file=sys.stderr)
        for sensor_id, v in aggregator.items():
            table = Table()
            for i in v:
                table.insert(*i)
            table = table.build()
            sensor: BaseSensorReadable = BUCKET_MAPPINGS[query.bucket](sensor_id, list(table.keys()), [])
            for entry in zip(*table.values()):
                sensor.rows.append(entry)
            yield sensor

