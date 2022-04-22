"""
TODO: Implement Readable and Writable classes
"""
import csv
import io
import datetime as dt
from typing import List, Dict, Any, Iterator, Tuple, Union

import bs4
import lxml.html as lh
import requests

from .base_wrapper import BaseSensor, BaseWrapper, correct_timestamp, BaseSensorWritable, BaseSensorReadable


class SCSensorReadable(BaseSensorReadable):
    def __init__(self, id_, header, rows):
        super().__init__(id_, header, rows)


class SCSensorWritable(BaseSensorWritable):

    def __iter__(self):
        return self.rows.__iter__()

    def __init__(self, id_, header, rows):
        super().__init__(id_, header, rows)
        self.correct_long_lat_in_header()


class SCSensor(BaseSensor):
    """Per sensor object designed to wrap csv objects returned by the SensorCommunity archives."""

    def __init__(self, id_, header=(), rows=()):
        super().__init__(id_, header, rows)

    @staticmethod
    def from_csv(sensor_id: str, csv_files: List[io.StringIO]) -> Any:
        """Factory method builds SCSensor from file like object
        containing csv data.

        :param sensor_id: id number of sensor
        :param csv_files: list of csv file like objects
        :return:
        """
        sensor = SCSensor(sensor_id)
        for csv_file in csv_files:
            reader = csv.reader(csv_file, delimiter=";")
            sensor.header = next(reader)
            for row in reader:
                # zip header and row then drop unwanted columns before committing row to sensor object
                dict_ = dict(zip(sensor.header, row))
                dict_.pop("sensor_id")
                dict_.pop("sensor_type")
                sensor.add_row(list(dict_.values()))
            # remove unwanted headers
            sensor.header.remove("sensor_id")
            sensor.header.remove("sensor_type")
        return sensor

    def get_writable(self):
        return SCSensorWritable(self.id, self.header, self.rows)


class SCWrapper(BaseWrapper):
    """API wrapper for the Sensor Community dashboard."""

    def __init__(self, username: str, password: str):
        self.__session, page = self.__login(username, password)
        self.__lookup_ids = list(self.__get_lookup_ids(page))

    def __get_lookup_ids(self, page: str) -> Iterator[str]:
        """Fetches look ids from the dashboard"""
        soup = bs4.BeautifulSoup(page, "lxml")
        # look for data button and extract lookup id from link inside
        for element in soup.find_all("a", {"class": "btn btn-sm btn-info"}):
            href = element.get("href")
            if href is not None:
                yield href.split("/")[2]

    def __login(self, username, password) -> Tuple[requests.Session, str]:
        """Handles logging in"""

        session = requests.Session()
        # fetching the csrf token for logging in
        res = session.get('https://devices.sensor.community/login')
        csrf_token = lh.fromstring(res.text).xpath('//input[@name="csrf_token"]/@value')[0]
        try:
            res = session.post('https://devices.sensor.community/login', allow_redirects=True,
                               data={"next": "",
                                     "csrf_token": csrf_token,
                                     "email": username,
                                     "password": password,
                                     "submit": "Login"})
        except IOError:
            raise IOError("Login failed")

        return session, res.text

    def get_sensor_ids(self) -> Dict[str, str]:
        """Gets the sensor's id and type using the lookup_id from dashboard"""

        sensor_ids = list()
        sensor_types = list()

        for id_ in self.__lookup_ids:
            res = self.__session.get(f'https://devices.sensor.community/sensors/{id_}/data')
            # Parse data stored between 1st <tr>..</tr> which itself is within the <table>..</table> of HTML
            doc = lh.fromstring(res.text)
            tr_elements = doc.xpath('//table/descendant::tr[1]')
            # First loop is retrieves sensor id
            # For each row, store each first element (header) and an empty list
            for t in tr_elements:
                # t[1] = element which holds the id
                data = t[1].text_content()[0:5]
                sensor_ids.append(data)
            # Second loop retrieves sensor type
            # Parse data that are stored between 1st <h2>..</h2> of HTML
            # For each row, store each first element (header) and an empty list
            for h in doc.xpath('//h2'):
                sensor_type = h.text_content()[-6:].strip()
                sensor_types.append(sensor_type.lower())

        return dict(zip(sensor_ids, sensor_types))

    @correct_timestamp
    def get_sensors(self, start: Union[dt.datetime, float, int], end: Union[dt.datetime, float, int],
                    sensors: Dict[str, str]) -> Iterator[SCSensor]:
        """Downloads the sensor data from the Earth sense dashboard and loads to SCSensor objects.

        :param sensors: dictionary mapping of {sensor_ids: sensor_types}
        :param start: start date
        :param end: end date
        :return: SCSensor objects containing scraped csv data
        """

        difference = end - start

        for id_, sensor_type in sensors.items():
            data = list()
            sensor_type = sensor_type.lower()

            for i in range(difference.days + 1):
                day = (start + dt.timedelta(days=i)).strftime("%Y-%m-%d")

                url = f'https://archive.sensor.community/{day}/{day}_{sensor_type}_sensor_{id_}.csv'
                res = requests.get(url, stream=True)
                if res.ok:
                    data.append(io.StringIO(io.BytesIO(res.content).read().decode('UTF-8')))
                else:
                    url = f'https://archive.sensor.community/{day}/{day}_{sensor_type}_sensor_{id_}_indoor.csv'
                    res = requests.get(url, stream=True)
                    if res.ok:
                        data.append(io.StringIO(io.BytesIO(res.content).read().decode('UTF-8')))

            yield SCSensor.from_csv(id_, data)
