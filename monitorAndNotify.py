#!usr/bin/python3
#imports
import json
from sense_hat import SenseHat
import datetime
import requests
import json
import sqlite3
import sys


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
currentDT = datetime.datetime.now()


#sensehat

sense = SenseHat()
sense.clear()

#gets temp and humid
temp  = sense.get_temperature()
temp_humid = sense.get_temperature_from_humidity()

dbName = 'THS.db'
conn = sqlite3.connect(dbName)
with conn: 
    cur = conn.cursor() 
    cur.execute("DROP TABLE IF EXISTS TEMP_HUMID_data")
    cur.execute("CREATE TABLE IF NOT EXIST TEMP_HUMID_data(timestamp DATETIME, temp NUMERIC, humid NUMERIC, notif DATETIME)")

def logData (temp, humid):	
    curs=conn.cursor()
    curs.execute("INSERT INTO TEMP_HUMID_data values(datetime('now'), (?))", (temp, ), (humid,))
    conn.commit()
    conn.close()

def addTemp():	
    if temp is not None:
        temp = round(temp, 1)
        logData (temp, temp_humid)

def select():
    curs=conn.cursor()
    for row in curs.execute("SELECT * FROM TEMP_HUMID_data"):
        print (row)
    conn.close()

ACCESS_TOKEN="o.90FuRwpaeFwBa2NaRKfshwjFhbi98emW"

def send_notification_via_pushbullet(title, body):
    """ Sending notification via pushbullet.
        Args:
            title (str) : title of text.
            body (str) : Body of text.
    """
    data_send = {"type": "note", "title": title, "body": body}
 
    resp = requests.post('https://api.pushbullet.com/v2/pushes', data=json.dumps(data_send),
                         headers={'Authorization': 'Bearer ' + ACCESS_TOKEN, 
                         'Content-Type': 'application/json'})
    if resp.status_code != 200:
        raise Exception('Something wrong')
    else:
        print('complete sending')

def sendNotif():
    if(temp > max_temp or temp < min_temp):
        send_notification_via_pushbullet("Temperature has exceeded", temp + "Degrees Celcius")
    if(temp_humid > max_humid or temp < min_humid):
        send_notification_via_pushbullet("Humidity has exceeded", temp_humid + "Degrees Celcius")    

#main function
def main():
    addTemp()
    sendNotif()

#Execute
main()
