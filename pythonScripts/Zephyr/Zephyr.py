import datetime
import json
from typing import List, Dict, Any

import pandas as pd

import requests



class APITimeoutException(Exception):
    pass


class ZephyrSensor:
    """Sensor class holds dictionary of dataframes and the sensor id"""

    def __init__(self, id_, df: pd.DataFrame):
        self.id = id_
        self.df = df

    @staticmethod
    def from_json(sensor_id: str, df: pd.DataFrame) -> Any:
        """Factory method builds PlumeSensor from file like object
        containing csv data.

        :param sensor_id: id number of sensor
        :param csv_file: csv file like object
        :return:
        """
    
        sensor = ZephyrSensor(sensor_id, df)

        return sensor
        
class ZephyrWrapper:
    """API wrapper for the Zephyr dashboard."""

    def __init__(self, username: str, password: str):
        self.username = username
        self.password = password


    def get_sensor_ids(self) -> List[str]:
        """Fetches sensor ids from Earthsense API """
        try:
            json_ = (requests.get(f"https://data.earthsense.co.uk/zephyrsForUser/{self.username}/{self.password}").json()['usersZephyrs'])
        except json.JSONDecodeError:
            return ['error']
        
        sensorList = []
        for key in json_:
            sensorList.append(json_[key]['zNumber'])

        print('✅: Fetching Sensorids Successful')

        return sensorList


    def get_sensor_data(self, sensors: List[str],
                        start: datetime.datetime, end: datetime.datetime,slot,formatting,target) -> List[ZephyrSensor]:
        """Downloads the sensor data from the Earthsense API and loads to ZephyrSensor objects.

        :param sensors: sensors to retrieve
        :param start: start time
        :param end: end time
        :return: List of ZephyrSensor objects for each sensor populated with data from the API
        """

        print('⚠️: Attempting Sensor CSV Retrieval. Please Wait')

        start = start.strftime("%Y%m%d%H%M") 
        end = end.strftime("%Y%m%d%H%M")

        sensorList = []

        for zephyr_id in sensors:
            url = f"https://data.earthsense.co.uk/dataForViewBySlots/{self.username}/{self.password}/{zephyr_id}/{start}/{end}/{slot}/def/{formatting}/{target}"
            print(url)
            res = requests.get(url)
            if res.ok:
                sensorList.append(ZephyrSensor.from_json(zephyr_id, self.json_to_dataframe(res.json()["slot"+slot])))
                
        print('✅: JSON Retrieval Successful')
        return sensorList

 
    def json_to_dataframe(self, json_):
        #TODO data split into dataframe dictionary 
        '''Extracts json into a dataframe '''

        #extracting and preparing the dataframe from the json objects
        df = pd.DataFrame.from_records(json_)
        df.drop('header', axis =0, inplace=True)
        df.drop('data_hash', axis =0, inplace=True)
        df.drop('UTS', axis=1, inplace=True)

        #explode function transform each element of a list to a row.
        #we can apply it to all the columns assuming they have the same number of elements in each list 
        df = df.apply(pd.Series.explode)

        # split path and strip string to extract sensor id
        return df
        

