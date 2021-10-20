import requests
from datetime import date, datetime, timedelta, timezone 
import pandas as pd

import io
from typing import List,Any,Dict

import lxml.html as lh
from requests.models import HTTPError

class ScSensor:
    """Sensor class holds dictionary of dataframes and the sensor id"""

    def __init__(self, id_, dictionary: Dict[int,pd.DataFrame]):
        self.id = id_
        self.dictionary = dictionary



class ScWrapper:
    """API wrapper for the Sensor Community dashboard."""

    
    def __init__(self, username: str, password: str):
        self.username = username
        self.password = password
        self.session = self.__login(username, password)

    def __login(self, username, password) -> requests.Session:
        '''Handles logging in and fetches lookids from the dashboard (webscaping)'''
        session = requests.Session()
     
        #fetching the csrf token for logging in  
        res = session.get('https://devices.sensor.community/login')
        doc = lh.fromstring(res.text)
        csrftoken = doc.xpath('//input[@name="csrf_token"]/@value')[0]
        print('✅: csrf token scraping Successful')

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
            print('🛑: Connection error. Rerun the code or check you connection')
            raise #TODO exit program on this exception 

        print('✅: Lookup_id Scraping Successful')
        return session


    def get_sensor_ids(self) -> Dict[str,str]:
        '''Gets the sensor's id and type (webscaping) using the lookupid from dashboard'''
        
        print('⚠️: Attempting Sensor Id And Type Scraping. Please Wait')

        #Create empty list for sensor ids
        sensorids = []
        sensortypes = []
    

        for id in self.lookupids:
            try:
                session = self.session
                
                res = session.get(f'https://devices.sensor.community/sensors/{id}/data')

                #Store the contents of the website under doc
                doc = lh.fromstring(res.text)

                '''This first loop is to get the sensor id'''
                #Parse data that are stored between 1st <tr>..</tr> which itself is within the <table>..</table> of HTML
                tr_elements = doc.xpath('//table/descendant::tr[1]')

                #For each row, store each first element (header) and an empty list
                for t in tr_elements:
                    #t[1] is the td element which holds the id
                    data= t[1].text_content()[0:5]
                    sensorids.append(data)

                '''This second loop is to get the sensor type'''
                #Parse data that are stored between 1st <h2>..</h2> of HTML
                h2_elements = doc.xpath('//h2')
                
                #For each row, store each first element (header) and an empty list
                for h in h2_elements:
                    sensortype = h.text_content()[-6:].strip()
                    sensortypes.append(sensortype)
                    
            
            except requests.exceptions.ConnectionError:
                print('🛑: Connection error. Rerun the code or check you connection')
                raise #TODO exit program on this exception

        sensors = dict(zip(sensorids, sensortypes))
        print('✅: Sensor Id And Type Scraping Successful')

        return sensors

    def get_sensor_data_csv(self, sensors: Dict[str,str], enddate: datetime, startdate: datetime) -> List[ScSensor]:

        print('⚠️: Attempting Sensor CSV Retrieval. Please Wait')

        '''Gets each sensor csv and appends each one into a dictioanry of dataframes. 
        This dictionary is used to intialise a sensorwhich is then itself appended into a list of sensors'''
       
        sensorList = []

        difference = enddate - startdate       

        for key in sensors:
            
            dataframeDict = {}
            sensortype = sensors[key].lower()
            id = key 

            for i in range(difference.days + 1):
                day = (startdate + timedelta(days=i))
                timestamp = int(day.replace(tzinfo=timezone.utc).timestamp())
                day = day.strftime("%Y-%m-%d")

                try:
                    url = f'https://archive.sensor.community/{day}/{day}_{sensortype}_sensor_{id}.csv'
                    res = requests.get(url, stream=True)

                    if res.ok:
                        dataframeDict[timestamp] = self.from_csv(res.content)

                    else:
                            url = f'https://archive.sensor.community/{day}/{day}_{sensortype}_sensor_{id}_indoor.csv'                            
                            res = requests.get(url, stream=True)

                            if res.ok:
                                dataframeDict[timestamp] = self.from_csv(res.content)
                                
                            else:
                                print(f'🛑: No sensor data available for this for sensor {id}, ({sensortype}) on the day: {day} ')
                                continue

                    print(url)
                except requests.exceptions.ConnectionError:
                    print('🛑: Connection error. Rerun the code or check you connection ')
                    raise #TODO exit program on this exception

            sensorList.append(ScSensor(id,dataframeDict))
           
        print('✅: CSV Retrieval Successful')
        return sensorList


    def from_csv(self, content: bytes) -> pd.DataFrame:
        '''Extracts csv into a dataframe using a buffer to avoid writing file to disk'''
        file_ = io.BytesIO(content)
        buffer = io.StringIO(file_.read().decode('UTF-8'))

        df = pd.read_csv(buffer, delimiter=';')

        return df
    
