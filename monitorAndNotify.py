#imports
import json
from sense_hat import SenseHat
import datetime

#readfile
with open('config.json', 'r') as myfile:
    data = myfile.read()

#parsefile
rangesData = json.loads(data)

#place data (range) from config.json to local variables
max_temp = rangesData['max_temp']
min_temp = rangesData['min_temp']
max_humid = rangesData['max_humid']
min_humid = rangesData['min_humid']

#get current time
#testing
currentDT = datetime.datetime.now()
    

#sensehat

sense = SenseHat()
sense.clear()

#gets temp and humid
temp  = sense.get_temperature()
temp_humid = sense.get_temperature_from_humidity()

