import requests
from datetime import date, datetime, timedelta, timezone 
import pandas as pd
import os
import io,csv
from typing import List,Any,Dict,Iterable

import json
import lxml.html as lh
from requests.models import HTTPError

class ScSensor:
    """Per sensor object designed to wrap the csv files returned by the Plume API.

    Example Usage:
        ps = PlumeSensor.from_csv("16397", open("sensor_measures_20211004_20211008_1.csv"))
        print(ps.DataFrame)
    """

    def __init__(self, id_, dictionary: Dict[int,pd.DataFrame]):
        self.id = id_
        self.dictionary = dictionary



class ScWrapper:
    """API wrapper for the Zephyr dashboard."""

    def __init__(self, username: str, password: str):
        self.username = username
        self.password = password
        self.session = self.__login(username, password)

    def __login(self, username, password) -> requests.Session:

        session = requests.Session()
     
        #fetching the csrf token for logging in  
        res = session.get('https://devices.sensor.community/login')
        doc = lh.fromstring(res.text)
        csrftoken = doc.xpath('//input[@name="csrf_token"]/@value')[0]
        print('csrf:' + csrftoken)

        #
        try:
            res = session.post('https://devices.sensor.community/login', allow_redirects=True ,data={"next":"", "csrf_token": csrftoken,"email": username, "password": password, "submit": "Login"})
            self.lookupids = []

            #Store the contents of the website under doc
            doc = lh.fromstring(res.text)
            #Parse data that are stored between <tr>..</tr> of HTML
            tr_elements = doc.xpath('//tr')

            for i in range(1, (len(tr_elements)-1)):
                T = tr_elements[i]
                for t in T.iterchildren():
                    data=t.text_content()
                    self.lookupids.append(data)
                    break
        
        except requests.exceptions.ConnectionError:
            print('Connection error')


        return session


    def get_sensor_ids(self) -> Dict[str,str]:

        print(self.lookupids)

        #Create empty list for sensor ids
        sensorids = []
        sensortypes = []
    

        for id in self.lookupids:
            try:
                session = self.session
                
                res = session.get(f'https://devices.sensor.community/sensors/{id}/data')

                #Store the contents of the website under doc
                doc = lh.fromstring(res.text)

                #Parse data that are stored between 1st <tr>..</tr> which itself is within the <table>..</table> of HTML
                tr_elements = doc.xpath('//table/descendant::tr[1]')

                #For each row, store each first element (header) and an empty list
                for t in tr_elements:
                    #t[1] is the td element which holds the id
                    data= t[1].text_content()[0:5]
                    sensorids.append(data)

                #Parse data that are stored between 1st <h2>..</h2> of HTML
                h2_elements = doc.xpath('//h2')
                
                #For each row, store each first element (header) and an empty list
                for h in h2_elements:
                    sensortype = h.text_content()[-6:].strip()
                    sensortypes.append(sensortype)
                    

            except requests.exceptions.ConnectionError:
                print('Connection error')
                return []

            #TODO remove break
            break


        sensors = dict(zip(sensorids, sensortypes))

        return sensors

    def get_sensor_data_csv(self, sensors: Dict[str,str], enddate: datetime, startdate: datetime) -> List[ScSensor]:
        
        # startdate = startdate - timedelta(days=1)
        # startdate = startdate.strftime("%Y-%m-%d")

        sensorList = []
       

        difference = enddate - startdate       # as timedelta

        for key in sensors:
            
            dataframeDict = {}
            sensortype = sensors[key].lower()
            id = key 

            #TODO for each day get csv link. extract dataframe and then add to a dictionary of dataframes or append into multi-index dataframe
            # Then intialise a sensor with the multi index dataframe  

            for i in range(difference.days + 1):
                day = (startdate + timedelta(days=i))
                timestamp = int(day.replace(tzinfo=timezone.utc).timestamp())
                day = day.strftime("%Y-%m-%d")

                try:
                    url = f'https://archive.sensor.community/{day}/{day}_{sensortype}_sensor_{id}.csv'
                    print(url)
                    res = requests.get(url, stream=True)

                    if res.ok:
                        dataframeDict[timestamp] = self.from_csv(res.content)

                    else:
                            url = f'https://archive.sensor.community/{day}/{day}_{sensortype}_sensor_{id}_indoor.csv'
                            print(url)
                            res = requests.get(url, stream=True)

                            if res.ok:
                                dataframeDict[timestamp] = self.from_csv(res.content)
                                
                            else:
                                print('no sensor data available')
                
                except requests.exceptions.ConnectionError:
                    print(ConnectionError)


            sensorList.append(ScSensor(id,dataframeDict))
            #TODO remove break
            break

        return sensorList


    def from_csv(self, content: bytes) -> pd.DataFrame:
  
        file_ = io.BytesIO(content)
        buffer = io.StringIO(file_.read().decode('UTF-8'))

        df = pd.read_csv(buffer, delimiter=';')

        return df
    
