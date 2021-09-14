import wget # pip install wget
import zipfile
import os

class PlumeDownload:

    sensorPaths = {}
    sensorIds = []
    path = ""

    def __init__(self,path):
        self.path = path

    @staticmethod
    def DownloadFile():

        sensorDirectory = ""
        directory = ""
        
        # Checking the status of URL
        url = open(path, "r").read()
        print(url)
        # Download and extraction 
        try: 
            target = wget.download(url, "..\..\data\zipfiles")
            #extract zip file on successful download
            with zipfile.ZipFile(target, "r") as zip_ref:
                zip_ref.extractall("..\..\data")
            timestampPath = target.split("/",1)[1] 
            timestampPath = timestampPath.split(".zip",1)[0] 

            directory = "..\..\data\\flow\\{}".format(timestampPath)
            sensorDirectory = next(os.walk(directory))[1]

        except BaseException as error:
            print('An exception occurred: {}'.format(error))

        return directory, sensorDirectory

    @staticmethod
    def extractCsvPaths(directory, sensorDirectory):
        sensorIds = []
        sensorPaths = []

        for currentId in sensorDirectory:
            sensorIds.append(currentId.split("_")[1])

        for snum in sensorIds:
            sensorPaths.append("\sensor_"  + snum)

        #extractCSV paths
        sensorPath = []
        for i in sensorPaths:
            sensorPath.append(os.path.join(directory + i))
        print(sensorPath)
        csvPaths = []

        for i in sensorPath:
            pair = []
            with os.scandir(i) as listOfFiles:
                for currentFile in listOfFiles:
                    # get all files that are csv
                    if currentFile.is_file() and currentFile.name.endswith('csv'):
                        pair.append(os.path.join(i,currentFile.name)) 

            csvPaths.append(pair)   

        
        # #map serial number to filepaths
        sensorPaths = {k:v for k,v in zip(sensorIds,csvPaths)}
        print(sensorPaths)

        return sensorIds,sensorPaths


p1 = PlumeDownload("../../CypressAutomation/urls/url.txt")
#p1.extractCsvPaths(p1.DownloadFile())



p1.extractCsvPaths("..\..\data\\flow\\task_269_1631186201", ['sensor_16397', 'sensor_17539', 'sensor_18699'])

#p1.extractCsvPaths("..\..\data\\flow\\temp", ['sensor_18720', 'sensor_18749', 'sensor_18699'])