import csv
import datetime
import json
import pathlib
import time
import io
from typing import List, Dict, Any, Generator, Iterable

import pandas as pd
#import zipfile

import requests

# from pythonScripts.SensorCommunity.mainCopy import USERNAME
# from pythonScripts.main import PASSWORD


class APITimeoutException(Exception):
    pass


class ZephyrSensor:
    """Per sensor object designed to wrap the csv files returned by the Plume API.

    Example Usage:
        ps = PlumeSensor.from_csv("16397", open("sensor_measures_20211004_20211008_1.csv"))
        print(ps.DataFrame)
    """

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
        try:
            json_ = (requests.get(f"https://data.earthsense.co.uk/zephyrsForUser/{self.username}/{self.password}").json()['usersZephyrs'])
        except json.JSONDecodeError:
            return ['error']
        
        sensorList = []
        for key in json_:
            sensorList.append(json_[key]['zNumber'])

        return sensorList


    def get_sensor_data(self, sensors: List[str],
                        start: datetime.datetime, end: datetime.datetime,slot,formatting,target) -> List[ZephyrSensor]:
        """Downloads the sensor data from the Zephyr API and loads to ZephyrSensor objects.

        :param sensors: sensors to retrieve
        :param start: start time
        :param end: end time
        :return: Generator of ZephyrSensor Objects for each sensor populated with data from the API
        """
        start = start.strftime("%Y%m%d%H%M") 
        end = end.strftime("%Y%m%d%H%M")

        sensorList = []

        #!!!!
        sensors = ['814','821']

        for zephyr_id in sensors:
            print(f"https://data.earthsense.co.uk/dataForViewBySlots/{self.username}/{self.password}/{zephyr_id}/{start}/{end}/{slot}/def/{formatting}/{target}")
            res = requests.get(f"https://data.earthsense.co.uk/dataForViewBySlots/{self.username}/{self.password}/{zephyr_id}/{start}/{end}/{slot}/def/{formatting}/{target}")
            if res.ok:

                sensorList.append(ZephyrSensor.from_json(zephyr_id, self.json_to_dataframe(res.json()["slot"+slot])))
                
        return sensorList

    #!!!! io.BytesIO() converts to bytes then we  https://stackoverflow.com/questions/42800250/difference-between-open-and-io-bytesio-in-binary-streams
    def json_to_dataframe(self, json_):
        """Download and extract zip into memory.

        :param link: url to sensor data zip file
        :return:sensor id, sensor data in a csv buffer
        """

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
        

