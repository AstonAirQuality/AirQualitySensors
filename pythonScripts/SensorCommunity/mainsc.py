import requests
from datetime import date, datetime, timedelta, timezone
import pandas as pd
import os
import io,csv
from typing import List,Iterable

from requests.models import Response


from SensorCommunity import ScWrapper

# TODO: Make environment variables
USERNAME = "190102421@aston.ac.uk"
PASSWORD = "RiyadtheWizard"
enddate = datetime.today() - timedelta(days=1)

import requests
import sys 
import lxml.html as lh

if __name__ == '__main__':
     
    scw = ScWrapper(USERNAME, PASSWORD)
    
    sensors = scw.get_sensor_data_csv(scw.get_sensor_ids(), enddate, startdate= datetime(2021, 10, 18))
    
    #sensors = scw.get_sensor_data_csv({'66007': 'SDS011'}, enddate, startdate= datetime(2021, 10, 18))

    # for sensor in sensors:
    #     print(sensor.id)
    #     for key in sensor.dictionary:
    #         print(sensor.dictionary[key].head())


