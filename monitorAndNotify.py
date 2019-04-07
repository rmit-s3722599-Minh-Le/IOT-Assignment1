#!/usr/bin/env python3
#imports
import json
from sense_hat import SenseHat
import datetime
import requests
import sqlite3
import sys
from datetime import date
from datetime import timedelta
import logging
import os



logging.basicConfig(filename = 'test.log', level=logging.DEBUG)

#readfile
# with open('config.json', 'r') as myfile:
#     data = myfile.read()

# #parsefile
# rangesData = json.loads(data)

# #place data (range) from config.json to local variables
# max_temp = rangesData['max_temp']
# min_temp = rangesData['min_temp']
# max_humid = rangesData['max_humid']
# min_humid = rangesData['min_humid']

# #get current time
# currentDT = datetime.datetime.now()


# #sensehat

# sense = SenseHat()
# sense.clear()

# #gets temp and humid
# temp  = round(sense.get_temperature(),1)
# temp_humid = round(sense.get_humidity(),1)

# dbName = 'THS.db'
# conn = sqlite3.connect(dbName)

class senseHatStuff:
    def __init__(self):
        sense = SenseHat()
        sense.clear()
        self.temp = round(sense.get_temperature(),1)
        self.temp_humid = round(sense.get_humidity(),1)
    
    def getTemp(self):
        return self.temp
    def getHumid(self):
        return self.temp_humid    
        
class getConfigData:
    def __init__(self):
        with open('config.json', 'r') as myfile:
            self.data = myfile.read()
            self.rangesData = json.loads(self.data)

    def getMaxT(self):
        max_temp = self.rangesData['max_temp']
        return max_temp
    def getMinT(self):
        min_temp = self.rangesData['min_temp']
        return min_temp
    def getMaxH(self):
        max_humid = self.rangesData['max_humid']
        return max_humid
    def getMinH(self):
        min_humid = self.rangesData['min_humid']
        return min_humid
    
class dataBase():
    def __init__(self, getConfigData, senseHatStuff, notification):
        self.dbName = 'THS.db'
        self.conn = sqlite3.connect(self.dbName)
        self.temp_humid = senseHatStuff.getHumid()
        self.temp = senseHatStuff.getTemp()
        self.notif = None
        self.notification = notification
        self.min_temp = getConfigData.getMinT()
        self.max_temp = getConfigData.getMaxT()
        self.min_humid = getConfigData.getMinH()
        self.max_humid = getConfigData.getMaxH()

    
    def createTable(self):
     with self.conn: 
         cur = self.conn.cursor() 
         cur.execute("CREATE TABLE IF NOT EXISTS TEMP_HUMID_data(timestamp DATETIME, temp NUMERIC, humid NUMERIC, notif DATETIME, date DATETIME)")
         logging.debug("table has been created")
    
    def select(self):
        conn = sqlite3.connect(self.dbName)
        curs=conn.cursor()
        for row in curs.execute("SELECT * FROM TEMP_HUMID_data"):
            print (row)
        conn.close()

    def logData (self, temp, humid, notif1, day):	
        curs=self.conn.cursor()
        curs.execute("INSERT INTO TEMP_HUMID_data values((?), (?), (?), (?), (?))", (datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S"),temp,humid,notif1,day))
        # logging.debug("temp: {}, humid: {}, notif: {}".format(temp,humid,notif1,day))
        self.conn.commit()
        self.conn.close()

    def getNotif(self):
        curs= self.conn.cursor()
        result = curs.execute("SELECT * FROM TEMP_HUMID_data ORDER BY timestamp DESC LIMIT 1").fetchone()
        try:
            pNotif = result[3]
        except:
            pNotif = date.today() - timedelta(days=1)
        logging.debug("notif: {}".format(pNotif))    
        return pNotif

    def checkNotif (self, temp, humid, notif, day):
        logging.debug(date.today().strftime("%d/%m/%Y"))
        if notif != date.today().strftime("%d/%m/%Y"):
            (self.notification).sendNotif(temp, self.temp_humid, self.min_humid, self.max_humid, self.min_temp, self.max_temp, self.getNotif())
            self.logData(temp, self.temp_humid, date.today().strftime("%d/%m/%Y"), day)
            # logging.debug("temp: {}, humid: {}, notif: {}".format(temp,humid,notif))
        else : 
            self.logData(temp, self.temp_humid, date.today().strftime("%d/%m/%Y"), day)
            # logging.debug("temp: {}, humid: {}, notif: {}".format(temp,humid,notif))
    
    def blah(self):
        self.notif = self.getNotif()
        if self.temp >= self.min_temp and self.temp <= self.max_temp : 
            if self.temp_humid >= self.min_humid and self.temp_humid <= self.max_humid :
                self.logData(self.temp, self.temp_humid, self.notif, date.today().strftime("%d/%m/%Y"))
                # logging.debug("temp: {}, humid: {}, notif: {}".format(temp,temp_humid,notif, date.today())
            else :
                self.checkNotif(self.temp, self.temp_humid, self.notif, date.today().strftime("%d/%m/%Y"))
                # logging.debug("temp: {}, humid: {}, notif: {}".format(temp,temp_humid,notif))
        else :
            if self.temp_humid > self.min_humid and self.temp_humid < self.max_humid:
                self.checkNotif(self.temp, self.temp_humid, self.notif, date.today().strftime("%d/%m/%Y"))
                # logging.debug("temp: {}, humid: {}, notif: {}".format(temp,temp_humid,notif))

            else :
                self.checkNotif(self.temp, self.temp_humid, self.notif, date.today().strftime("%d/%m/%Y"))
                # logging.debug("temp: {}, humid: {}, notif: {}".format(temp,temp_humid,notif))




class notification:
    

    def send_notification_via_pushbullet(self, title, body):
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
    

    def sendNotif(self, temp, temp_humid, min_humid, max_humid, max_temp, min_temp, getNotif):
        # if(temp > max_temp or temp < min_temp):
        #     send_notification_via_pushbullet("Temperature has exceeded", temp + "Degrees Celcius")
        # if(temp_humid > max_humid or temp_humid < min_humid):
        #     send_notification_via_pushbullet("Humidity has exceeded", temp_humid + "Degrees Celcius")
        if(temp > max_temp or temp < min_temp or temp_humid > max_humid or temp_humid < min_humid):
            logging.debug("tnotifsent")
            self.send_notification_via_pushbullet("Alert", "temp:" + str(temp) + " and humid: " + str(temp_humid) + str(getNotif) )     















  

#main function
def main():
    hat = senseHatStuff()
    config = getConfigData()
    notif = notification()
    base = dataBase(config,hat,notif)
    base.createTable()
    base.blah()



#Execute
main()
