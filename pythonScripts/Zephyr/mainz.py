import datetime
import pandas as pd
import numpy as np
import requests
import psycopg2
from datetime import date, datetime, timedelta, timezone
import os


from Zephyr import ZephyrWrapper

# TODO: Make environment variables
USERNAME = "AstonUniversity"
PASSWORD = "Xo08R83d43e0Kk6"
SLOTS = "B"
FORMAT = "json"
TARGET = "api"

if __name__ == '__main__':
    
    zw = ZephyrWrapper(USERNAME, PASSWORD)
   
    # sensors = zw.get_sensor_ids()
    # for sensor in sensors:
    #     print(sensor)

    sensors = zw.get_sensor_data(zw.get_sensor_ids(),
                                  start= datetime(2021, 9, 17),
                                  end= datetime(2021, 9, 20),
                                  slot = SLOTS,
                                  formatting = FORMAT,
                                  target = TARGET)

    # for sensor in sensors:
    #     print(sensor.id)
    #     print(sensor.df)

    
   
