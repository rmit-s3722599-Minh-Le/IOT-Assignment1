#!/usr/bin/env python3
#imports
import json
from sense_hat import SenseHat
import datetime
import requests
import json
import sqlite3
import sys
from datetime import date
from datetime import timedelta
import logging
import os



logging.basicConfig(filename = 'test.log', level=logging.DEBUG)

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
temp  = round(sense.get_temperature(),1)
temp_humid = round(sense.get_humidity(),1)

dbName = 'THS.db'
conn = sqlite3.connect(dbName)



with conn: 
    cur = conn.cursor() 
    cur.execute("CREATE TABLE IF NOT EXISTS TEMP_HUMID_data(timestamp DATETIME, temp NUMERIC, humid NUMERIC, notif DATETIME, date DATETIME)")
    logging.debug("table has been created")



def send_notification_via_pushbullet(title, body):
    ACCESS_TOKEN="o.90FuRwpaeFwBa2NaRKfshwjFhbi98emW"
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



def logData (temp, humid, notif1, day):	
    curs=conn.cursor()
    curs.execute("INSERT INTO TEMP_HUMID_data values((?), (?), (?), (?), (?))", (datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S"),temp,humid,notif1,day))
    # logging.debug("temp: {}, humid: {}, notif: {}".format(temp,humid,notif1,day))
    conn.commit()
    conn.close()

def getNotif ():
    curs= conn.cursor()
    result = curs.execute("SELECT * FROM TEMP_HUMID_data ORDER BY timestamp DESC LIMIT 1").fetchone()
    try:
        pNotif = result[3]
    except:
        pNotif = date.today() - timedelta(days=1)
    logging.debug("notif: {}".format(pNotif))    
    return pNotif




def blah():
    notif = getNotif()
    if temp > min_temp and temp < max_temp : 
        if temp_humid > min_humid and temp_humid < max_humid :
            logData(temp, temp_humid, notif, date.today())
            # logging.debug("temp: {}, humid: {}, notif: {}".format(temp,temp_humid,notif, date.today())
        else :
            checkNotif(temp, temp_humid, notif, date.today().strftime("%d/%m/%Y"))
            # logging.debug("temp: {}, humid: {}, notif: {}".format(temp,temp_humid,notif))
    else :
        if temp_humid > min_humid and temp_humid < max_humid:
            checkNotif(temp, temp_humid, notif, date.today().strftime("%d/%m/%Y"))
            # logging.debug("temp: {}, humid: {}, notif: {}".format(temp,temp_humid,notif))

        else :
            checkNotif(temp, temp_humid, notif, date.today().strftime("%d/%m/%Y"))
            # logging.debug("temp: {}, humid: {}, notif: {}".format(temp,temp_humid,notif))


def checkNotif (temp, humid, notif, day):
    logging.debug(date.today().strftime("%d/%m/%Y"))
    if notif != date.today().strftime("%d/%m/%Y"):
            sendNotif(temp, temp_humid)
            logData(temp, temp_humid, date.today().strftime("%d/%m/%Y"), day)
            # logging.debug("temp: {}, humid: {}, notif: {}".format(temp,humid,notif))
    else : 
            logData(temp, temp_humid, date.today().strftime("%d/%m/%Y"), day)
            # logging.debug("temp: {}, humid: {}, notif: {}".format(temp,humid,notif))



def select():
    conn = sqlite3.connect(dbName)
    curs=conn.cursor()
    for row in curs.execute("SELECT * FROM TEMP_HUMID_data"):
        print (row)
    conn.close()


def sendNotif(temp, temp_humid):
    # if(temp > max_temp or temp < min_temp):
    #     send_notification_via_pushbullet("Temperature has exceeded", temp + "Degrees Celcius")
    # if(temp_humid > max_humid or temp_humid < min_humid):
    #     send_notification_via_pushbullet("Humidity has exceeded", temp_humid + "Degrees Celcius")
    if(temp_humid > max_humid or temp < min_humid or temp_humid > max_humid or temp_humid < min_humid):
        logging.debug("tnotifsent")
        send_notification_via_pushbullet("Alert", "temp:" + str(temp) + " and humid: " + str(temp_humid) + str(getNotif()) )       

#main function
def main():
    blah()

#Execute
main()
