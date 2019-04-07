#!/usr/bin/env python3
import bluetooth
import time
import subprocess as sp
import os
import json
from sense_hat import SenseHat
import datetime
from datetime import date
import requests

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
        if(self.temp>self.min_temp and self.temp<self.max_temp):
            if(self.temp_humid>self.min_humid and self.temp_humid<self.max_humid):
                self.send_notification_via_pushbullet(date.now.strftime("%H"), ("temperature: {}, humidity: {}, no breaches.").format(self.temp, self.temp_humid))
            else:
                self.send_notification_via_pushbullet(date.now.strftime("%H"), ("temperature: {}, humidity: {}, there is a breach in humidity.").format(self.temp, self.temp_humid))
        else:
            if(self.temp_humid>self.min_humid and self.temp_humid<self.max_humid):
                self.send_notification_via_pushbullet(date.now.strftime("%H"), ("temperature: {}, humidity: {}, there is a breach in temperature.").format(self.temp, self.temp_humid))
            else:
                self.send_notification_via_pushbullet(date.now.strftime("%H"), ("temperature: {}, humidity: {}, there is a breach in temperature and in humidity.").format(self.temp, self.temp_humid))
    


def getPairedDevices():
    p = sp.Popen(["bt-device", "--list"], stdin = sp.PIPE, stdout = sp.PIPE, close_fds = True)
    (stdout, stdin) = (p.stdout, p.stdin)

    datas = stdout.readlines()
    return datas

class timer:
    def __init__(self):
        self.timing = False
        self.notifTime = None
        self.alist = []
    
    def stamp(self):
        if (self.timimg == False):
            self.notifTime = date.now.strftime("%H") 
            self.timimg = True

    def newFrame(self):
        if(self.notifTime == date.now.strftime("%H") ):
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
    nearbyDevices = bluetooth.discover_devices()

    for macAddress in nearbyDevices:
        for data in getPairedDevices():
                s_data = data.decode('ascii')
                istart = s_data.rfind('(')
                iend = s_data.rfind(')')
                pairedDeviceAddress = s_data[istart + 1,iend - 1]

                if(pairedDeviceAddress == macAddress):
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
    compareTime = timer()
    while True:
        scanning(compareTime)

main()
