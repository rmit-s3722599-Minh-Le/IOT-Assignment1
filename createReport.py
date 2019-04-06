#!/usr/bin/env python3
import sqlite3
import requests
import json
import csv

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

class tempCompare:
    def __init__(self, max_temp, min_temp, max_humid,min_humid):
        self.max_temp_breach = False
        self.min_temp_breach = False
        self.max_humid_breach = False
        self.min_humid_breach = False

        self.c_max_temp = 0
        self.c_min_temp = 100
        self.c_max_humid = 0
        self.c_min_humid = 100
        self.max_temp = max_temp
        self.min_temp = min_temp
        self.max_humid = max_humid
        self.min_humid = min_humid

    def compareTemp(self, temp):
        if(temp > self.max_temp):
            self.max_temp_breach = True
            if(temp > self.c_max_temp):
                self.c_max_temp = temp
        else:
            if(temp < self.min_temp):
                self.min_temp_breach = True
                if(temp < self.c_min_temp):
                    self.c_min_temp = temp
            
    def compareHumid(self, humid):
        if(humid > self.max_humid):
            self.max_humid_breach = True
            if(humid > self.c_max_humid):
                self.c_max_humid = humid
        else:
            if(humid < self.min_humid):
                self.min_humid_breach = True
                if(humid < self.c_min_humid):
                    self.c_min_humid = humid

    def getResult(self, date):
        resultString = ""
        aboveTemp = self.c_max_temp - self.max_temp
        belowTemp = self.c_min_temp - self.min_temp
        aboveHumid = self.c_max_humid - self.max_humid
        belowHumid = self.c_min_humid - self.min_humid 
        if(min_temp_breach = True and max_temp_breach = True and min_humid_breach = True and max_humid_breach = True):
            resultString = "BAD: {}*C below minimum temperature and {}*C above maximum temperature and {} %% below minimum humidity and {} %% above maximum humidity".format(belowTemp, aboveTemp, belowHumid, aboveHumid)
        if(min_temp_breach = True and max_temp_breach = True and min_humid_breach = True and max_humid_breach = False):
            resultString = "BAD: {}*C below minimum temperature and {}*C above maximum temperature and {} %% below minimun humidity".format(belowTemp, aboveTemp, belowHumid)
        if(min_temp_breach = True and max_temp_breach = True and min_humid_breach = False and max_humid_breach = True):
            resultString = "BAD: {}*C below minimum temperature and {}*C above maximum temperature and {} %% above maximum humidity".format(belowTemp, aboveTemp, aboveHumid)
        if(min_temp_breach = True and max_temp_breach = True and min_humid_breach = False and max_humid_breach = False):
            resultString = "BAD: {}*C below minimum temperature and {}*C above maximum temperature".format(belowTemp, aboveTemp)
        if(min_temp_breach = True and max_temp_breach = False and min_humid_breach = True and max_humid_breach = True):
            resultString = "BAD: {}*C below minimum temperature and {} %% below minimum humidity and {} %% above maximum humidity".format(belowTemp, belowHumid, aboveHumid)
        if(min_temp_breach = True and max_temp_breach = False and min_humid_breach = True and max_humid_breach = False):
            resultString = "BAD: {}*C below minimum temperature and {} %% below minimum humidity".format(belowTemp, belowHumid)
        if(min_temp_breach = True and max_temp_breach = False and min_humid_breach = False and max_humid_breach = True):
            resultString = "BAD: {}*C below minimum temperature and {} %% above maximum humidity".format(belowTemp, aboveHumid)
        if(min_temp_breach = True and max_temp_breach = False and min_humid_breach = False and max_humid_breach = False):
            resultString = "BAD: {}*C below minimum temperature".format(belowTemp)
        if(min_temp_breach = False and max_temp_breach = True and min_humid_breach = True and max_humid_breach = True):
            resultString = "BAD: {}*C above maximum temperature and {} %% below minimum humidity and {} %% above maximum humidity".format(aboveTemp, belowHumid, aboveHumid)
        if(min_temp_breach = False and max_temp_breach = True and min_humid_breach = True and max_humid_breach = False):
            resultString = "BAD: {}*C above maximum temperature and {} %% below minimum humidity".format(aboveTemp, belowHumid)
        if(min_temp_breach = False and max_temp_breach = True and min_humid_breach = False and max_humid_breach = True):
            resultString = "BAD: {}*C above maximum temperature and {} %% above maximum humidity".format(aboveTemp, aboveHumid)
        if(min_temp_breach = False and max_temp_breach = True and min_humid_breach = False and max_humid_breach = False):
            resultString = "BAD: {}*C above maximum temperature".format(aboveTemp)
        if(min_temp_breach = False and max_temp_breach = False and min_humid_breach = True and max_humid_breach = True):
            resultString = "BAD: {} %% below minimum humidity and {} %% above maximum humidity".format(belowHumid, aboveHumid)
        if(min_temp_breach = False and max_temp_breach = False and min_humid_breach = True and max_humid_breach = False):
            resultString = "BAD: {} %% below minimum humidity".format(belowHumid)
        if(min_temp_breach = False and max_temp_breach = False and min_humid_breach = False and max_humid_breach = True):
            resultString = "BAD: {} %% above maximum humidity".format(aboveHumid)
        if(min_temp_breach = False and max_temp_breach = False and min_humid_breach = False and max_humid_breach = False):
            resultString = "OK"
        return resultString


    def reset(self):
        self.max_temp_breach = False
        self.min_temp_breach = False
        self.max_humid_breach = False
        self.min_humid_breach = False
        self.c_max_temp = 0
        self.c_min_temp = 100
        self.c_max_humid = 0
        self.c_min_humid = 100



def getdata(conn, getConfigData):
    createFile()
    curs = conn.cursor()
    rows = curs.execute("SELECT * FROM TEMP_HUMID_data ORDER BY timestamp").fetchall()
    checkDate = None
    tempComp = tempCompare(getConfigData.getMaxT(), getConfigData.getMinT, getConfigData.getMaxH, getConfigData.getMinH) 
    for row in rows:
        if checkDate == None:
            checkDate = row[4] 
        else:
            if checkDate == row[4]:
                tempComp.compareTemp(row[1])
                tempComp.compareHumid(row[2])
            else:
                addToCSV(tempComp.getResult(), checkDate)
                checkDate = row[4]
                tempComp.reset()
                tempComp.compareTemp(row[1])
                tempComp.compareHumid(row[2])
                        
    conn.commit()
    conn.close()          
 


                
def addToCSV(breachMessage, date):
    with open('report.csv', 'a') as csvfile:
        filewriter = csv.writer(csvfile)
        filewriter.writerows([date, breachMessage])
        
def createFile():
    with open('report.csv', 'wb') as myfile:





def main():
    conn = sqlite3.connect('THs.db')
    getdata(conn, getConfigData())  



main()



