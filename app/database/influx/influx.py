import itertools
import os
import datetime as dt
import timeit
from collections import defaultdict

from influxdb_client import InfluxDBClient, WriteOptions, Point, Dialect

from app.api_wrappers.base_wrapper import BaseSensor
from app.api_wrappers.plume_wrapper import PlumeSensor
from app.api_wrappers.sensor_community_wrapper import SCSensor
from app.api_wrappers.zephyr_wrapper import ZephyrSensor
from app.database.influx.query_builder import InfluxQueryBuilder

BUCKET_MAPPINGS = {"plume": PlumeSensor, "zephyr": ZephyrSensor, "sensor_community": SCSensor}


class Table:
    """
    TODO: Migrate to a filtered base sensor object
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
        self.asset = None
        self.fields = set()
        self.index = defaultdict(list)  # {"timestamp": [field0, field1, fieldN, ...]}
        self.data = defaultdict(list)  # {"timestamp": [{"measurement": "AMU", "field": "mean", "value": "01"}, ...]}
        self.corrected = False

    def insert(self, timestamp: str, measurement: str, field: str, value: float, sensor_id: int):
        """
        Insert entry into table. The entry is inserted into the internal index and data structure.
        If the table has already been built all subsequent inserts are ignored.
        """
        if self.corrected:
            return
        if self.asset is None:
            self.asset = measurement
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
            base["measurement"].append(self.asset)
            for i in v:
                base[i["field"]].append(i["value"])
        return dict(base)


class Influx:

    @staticmethod
    def get_client(url=os.getenv("INFLUXDB_V2_URL"), org=os.getenv("INFLUXDB_V2_ORG"),
                   token=os.getenv("INFLUXDB_V2_TOKEN")):
        return InfluxDBClient(url=url, org=org, token=token)

    @staticmethod
    def write(bucket: str, sensor_data: BaseSensor, measurement="air_quality", client=None):
        # select static client if no client is specified by the user, helps with testability
        writer = (Influx.get_client() if client is None else client).write_api(
            write_options=WriteOptions(batch_size=50_000, flush_interval=10_000))
        for entry in sensor_data:
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
    def read(query: InfluxQueryBuilder, client=None):
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
        start = timeit.default_timer()
        csv_buffer = list(reader.query_csv(query.build(), dialect=Dialect()))
        end = timeit.default_timer()
        print(f"DB READ TIME {end - start}s")
        if len(csv_buffer) < 3:
            return []
        headers = csv_buffer[0]
        aggregator = defaultdict(list)
        for line in itertools.islice(csv_buffer, 1, None):
            dict_ = dict(zip(headers, line))
            try:
                sensor_id = int(dict_["sensor_id"])
            except KeyError:
                continue
            try:
                aggregator[sensor_id].append([dict_["_time"], dict_["_measurement"], dict_["_field"],
                                              float(dict_["_value"])])
            except ValueError:
                aggregator[sensor_id].append([dict_["_time"], dict_["_measurement"], dict_["_field"],
                                              dict_["_value"]])
        for sensor_id, v in aggregator.items():
            table = Table()
            for i in v:
                table.insert(*i, sensor_id)
            table = table.build()
            sensor: BaseSensor = BUCKET_MAPPINGS[query.bucket](sensor_id, table.keys(), [])
            for entry in table.values():
                for i in entry:
                    # append to internal data structure and skip extra processing
                    sensor.rows.append(i)
            yield sensor
