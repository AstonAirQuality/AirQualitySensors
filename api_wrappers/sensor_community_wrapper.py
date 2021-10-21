import requests
from datetime import datetime, timedelta, timezone
import io
from typing import List, Dict, Any, Iterable, Iterator
import csv

import lxml.html as lh

from api_wrappers.base_wrapper import BaseSensor, BaseWrapper


class ScSensor(BaseSensor):
    """Per sensor object designed to wrap csv objects returned by the SensorCommunity Archives."""

    def __init__(self, id_, header=(), row=()):
        super().__init__(id_, header, row)

    def add_row(self, row: Iterable):
        self.rows.append([int(i) if str(i).isdigit() else i for i in row])

    @property
    def pollutants(self):
        """Returns pollutants found in the header.
        """
        return self.header[2:]

    @staticmethod
    def from_csv(sensor_id: str, csv_fileList: List[io.StringIO]) -> Any:
        """Factory method builds ScSensor from file like object
        containing csv data.

        :param sensor_id: id number of sensor
        :param csv_file: csv file like object
        :return:
        """
        sensor = ScSensor(sensor_id, [], [])

        for csv_file in csv_fileList:
            reader = csv.reader(csv_file, dialect=csv.unix_dialect)
            sensor.header = next(reader)
            for row in reader:
                sensor.add_row(row)

        return sensor


class ScWrapper(BaseWrapper):
    """API wrapper for the Sensor Community dashboard."""

    def __init__(self, username: str, password: str):
        self.username = username
        self.password = password
        self.session = self.__login(username, password)

    def __login(self, username, password) -> requests.Session:
        """Handles logging in and fetches look ids from the dashboard (webscaping)"""

        session = requests.Session()

        # fetching the csrf token for logging in
        res = session.get('https://devices.sensor.community/login')
        doc = lh.fromstring(res.text)
        csrftoken = doc.xpath('//input[@name="csrf_token"]/@value')[0]

        try:
            res = session.post('https://devices.sensor.community/login', allow_redirects=True,
                               data={"next": "", "csrf_token": csrftoken, "email": username, "password": password,
                                     "submit": "Login"})
            self.lookupids = []

            # Store the contents of the website under doc
            doc = lh.fromstring(res.text)
            # Parse data that are stored between <tr>..</tr> of HTML
            tr_elements = doc.xpath('//tr')

            for i in range(1, (len(tr_elements) - 1)):
                T = tr_elements[i]
                for t in T.iterchildren():
                    data = t.text_content()
                    self.lookupids.append(data)
                    break

        except requests.exceptions.ConnectionError:
            raise  # TODO exit program on this exception

        return session

    def get_sensor_ids(self) -> Dict[str, str]:
        '''Gets the sensor's id and type (webscaping) using the lookupid from dashboard'''

        # Create empty list for sensor ids
        sensorids = []
        sensortypes = []

        for id in self.lookupids:
            try:
                session = self.session

                res = session.get(f'https://devices.sensor.community/sensors/{id}/data')

                # Store the contents of the website under doc
                doc = lh.fromstring(res.text)

                '''This first loop is to get the sensor id'''
                # Parse data that are stored between 1st <tr>..</tr> which itself is within the <table>..</table> of HTML
                tr_elements = doc.xpath('//table/descendant::tr[1]')

                # For each row, store each first element (header) and an empty list
                for t in tr_elements:
                    # t[1] is the td element which holds the id
                    data = t[1].text_content()[0:5]
                    sensorids.append(data)

                '''This second loop is to get the sensor type'''
                # Parse data that are stored between 1st <h2>..</h2> of HTML
                h2_elements = doc.xpath('//h2')

                # For each row, store each first element (header) and an empty list
                for h in h2_elements:
                    sensortype = h.text_content()[-6:].strip()
                    sensortypes.append(sensortype)


            except requests.exceptions.ConnectionError:
                raise  # TODO exit program on this exception

        sensors = dict(zip(sensorids, sensortypes))

        return sensors

    def get_sensors(self, sensors: Dict[str, str], enddate: datetime, startdate: datetime) -> Iterator[ScSensor]:

        '''Gets each sensor csv and appends each one into a dictioanry of dataframes. 
        This dictionary is used to intialise a sensorwhich is then itself appended into a list of sensors'''

        difference = enddate - startdate

        for key in sensors:

            dataList = []
            sensortype = sensors[key].lower()
            id_ = key

            for i in range(difference.days + 1):
                day = (startdate + timedelta(days=i))
                timestamp = int(day.replace(tzinfo=timezone.utc).timestamp())
                day = day.strftime("%Y-%m-%d")

                try:
                    url = f'https://archive.sensor.community/{day}/{day}_{sensortype}_sensor_{id_}.csv'
                    res = requests.get(url, stream=True)

                    if res.ok:
                        dataList.append(io.StringIO(io.BytesIO(res.content).read().decode('UTF-8')))
                    else:
                        url = f'https://archive.sensor.community/{day}/{day}_{sensortype}_sensor_{id_}_indoor.csv'
                        res = requests.get(url, stream=True)

                        if res.ok:
                            dataList.append(io.StringIO(io.BytesIO(res.content).read().decode('UTF-8')))
                        else:
                            print(
                                f'🛑: No sensor data available for this for sensor {id}, ({sensortype}) on the day: {day} ')
                            continue


                except requests.exceptions.ConnectionError:
                    raise  # TODO exit program on this exception

            yield ScSensor.from_csv(id_, dataList)
