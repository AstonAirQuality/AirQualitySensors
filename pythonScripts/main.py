import datetime

from pythonScripts.plume_api_wrapper import PlumeWrapper

# TODO: Make environment variables
EMAIL = "180086320@aston.ac.uk"
PASSWORD = "aston1234"

if __name__ == '__main__':
    pw = PlumeWrapper(EMAIL, PASSWORD, 85)
    sensors = pw.get_sensor_data(pw.get_sensor_ids(),
                                 start=datetime.datetime(2021, 9, 30),
                                 end=datetime.datetime(2021, 10, 13))
    for sensor in sensors:
        print(sensor.id)
