#!/usr/bin/env python3
import bluetooth
import time
import subprocess as sp
import os
import json
from sense_hat import SenseHat
import datetime
import requests
import logging



logging.basicConfig(filename = 'gbttest.log', level=logging.DEBUG)


class getConfigData:
    print("data is imported from json")
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

class senseHatStuff:
    def __init__(self):
        print("getting temperature")
        sense = SenseHat()
        sense.clear()
        self.temp = round(sense.get_temperature(),1)
        self.temp_humid = round(sense.get_humidity(),1)
    
    def getTemp(self):
        return self.temp
    def getHumid(self):
        return self.temp_humid    

class bullet:
    def __init__(self, getConfigData, senseHatStuff):
        self.temp_humid = senseHatStuff.getHumid()
        self.temp = senseHatStuff.getTemp()
        self.min_temp = getConfigData.getMinT()
        self.max_temp = getConfigData.getMaxT()
        self.min_humid = getConfigData.getMinH()
        self.max_humid = getConfigData.getMaxH()

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

    def sendNotif(self):
        print("sendNotif activated")
        if(self.temp>self.min_temp and self.temp<self.max_temp):
            if(self.temp_humid>self.min_humid and self.temp_humid<self.max_humid):
                self.send_notification_via_pushbullet(datetime.datetime.now().strftime("%H"), ("temperature: {}, humidity: {}, no breaches.").format(self.temp, self.temp_humid))
            else:
                self.send_notification_via_pushbullet(datetime.datetime.now().strftime("%H"), ("temperature: {}, humidity: {}, there is a breach in humidity.").format(self.temp, self.temp_humid))
        else:
            if(self.temp_humid>self.min_humid and self.temp_humid<self.max_humid):
                self.send_notification_via_pushbullet(datetime.datetime.now().strftime("%H"), ("temperature: {}, humidity: {}, there is a breach in temperature.").format(self.temp, self.temp_humid))
            else:
                self.send_notification_via_pushbullet(datetime.datetime.now().strftime("%H"), ("temperature: {}, humidity: {}, there is a breach in temperature and in humidity.").format(self.temp, self.temp_humid))
            logging.debug("notif is sent")
    


def getPairedDevices():
    p = sp.Popen(["bt-device", "--list"], stdin = sp.PIPE, stdout = sp.PIPE, close_fds = True)
    (stdout, stdin) = (p.stdout, p.stdin)
    datas = stdout.readlines()
    print("getting paired devices")
    logging.debug("the data: {}".format(datas))
    return datas

class timer:
    def __init__(self):
        self.timing = False
        self.notifTime = None
        self.alist = []
    
    def stamp(self):
        if (self.timimg == False):
            self.notifTime = datetime.datetime.now().strftime("%H") 
            self.timimg = True

    def newFrame(self):
        if(self.notifTime == datetime.datetime.now().strftime("%H") ):
            self.timimg = False
            self.clearList()

    def getList(self):
        return self.alist
    
    def addtoList(self, address):
        self.alist.append(address)
    
    def clearList(self):
        self.alist.clear()
        
           

def scanning(timer):
    gCD = getConfigData()
    senseHatS = senseHatStuff()
    bull = bullet(gCD,senseHatS)
    #scanning
    print("scanning devices..")
    logging.debug("scanning nearby devices")
    nearbyDevices = bluetooth.discover_devices()
    print("starting scan")
    for macAddress in nearbyDevices:
        logging.debug("macAdress of a device:{}".format(macAddress.decode('ascii')))
        logging.debug("macAdress of a device:")
        logging.debug(macAddress)
        print("pair devices sart")
        for data in getPairedDevices():
            logging.debug("macAdress of a device:{}, paired device: {}".format(macAddress.decode('ascii'), data))
            s_data = data.decode('ascii')
            istart = s_data.rfind('(')
            iend = s_data.rfind(')')
            pairedDeviceAddress = s_data[istart + 1,iend - 1]

            if(pairedDeviceAddress == macAddress.decode('ascii')):
                if pairedDeviceAddress not in timer.getList():
                    timer.addtoList(pairedDeviceAddress)
                    bull.sendNotif()
                    timer.stamp()
    timer.newFrame()
    time.sleep(10)





#temp exceed humid exceeds
#temp exceeds humid within
#temp within humid within
#temp within humid exceeds




def main():
    logging.debug("the date00: {}".format(datetime.datetime.now().strftime("%H")))
    logging.debug("the date 01: {}".format(datetime.datetime.now()))
    logging.debug("starting python bluetooth file")
    compareTime = timer()
    while True:
        scanning(compareTime)

main()
