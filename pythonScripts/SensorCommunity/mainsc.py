import requests
from datetime import date, datetime, timedelta, timezone
import pandas as pd
import os
import io,csv
from typing import List,Iterable

from requests.models import Response



from SensorCommunity import ScWrapper

# TODO: Make environment variables
STARTDATE = (date.today() - timedelta(days=1)).strftime("%Y-%m-%d")
sensortype = "sds011"
#sensorid = "60362" #"60368"

USERNAME = "190102421@aston.ac.uk"
PASSWORD = "RiyadtheWizard"


import requests
import sys 
import lxml.html as lh

if __name__ == '__main__':
     
    # scw = ScWrapper(USERNAME, PASSWORD)
    # print(scw.get_sensor_ids())

#TODO try check each sensor if a csv file exists (catch Connection error). if it doesn't http 404 look for indoor version. if it still fails then raise error (sensor data missing from archives)
# get sensor csv. put into buffer and write to sensor class.

    scw = ScWrapper(USERNAME, PASSWORD)
    enddate = datetime.today() - timedelta(days=1)
    #sensors = scw.get_sensor_data_csv(scw.get_sensor_ids(), enddate, startdate= datetime(2021, 10, 18))
    
    sensors = scw.get_sensor_data_csv({'66007': 'SDS011'}, enddate, startdate= datetime(2021, 10, 18))

    for sensor in sensors:
        for key in sensor.dictionary:
            print(sensor.dictionary[key].head())

    # for sensor in sensors:
    #     print(sensor.id)
    #     print(sensor.df)

