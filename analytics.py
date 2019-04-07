import pandas as pd
from pandas.tools.plotting import table
import sqlite3
import os
import matplotlib as mpl
if os.environ.get('DISPLAY','') == '':
    print('no display found. Using non-interactive Agg backend')
    mpl.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sb
import time



class getData():
    def __init__(self):
        self.dbName = 'THS.db'
        self.conn = sqlite3.connect(self.dbName)
        self.curs = self.conn.cursor()
        self.alist = []

    def getTempCol(self):
        tempList = self.curs.execute("SELECT * FROM TEMP_HUMID_data ORDER BY timestamp").fetchall()
        aList = []
        for row in tempList:
            aList.append(row[1])
        return aList

    def getHumidCol(self):
        humidList = self.curs.execute("SELECT * FROM TEMP_HUMID_data ORDER BY timestamp").fetchall() 
        aList = []
        for row in humidList:
            aList.append(row[2])
        return aList
    def getTempColWithPand(self):
        df = pd.read_sql_query("SELECT temp FROM TEMP_HUMID_data", self.conn)
        return df
    
    def getHumidColWithPand(self):
        
        df = pd.read_sql_query("SELECT humid FROM TEMP_HUMID_data", self.conn)
        return df


def createImageWithLibraryMat(x):
    temp = x['temp']
    bins = [10,12,14,16,18,20,22,24,26,28,30,32,34,36,38,40,42,44,46,48,50]
    plt.hist(temp, bins, histtype = 'bar', rwidth=0.8)
    plt.xlabel('temp')
    plt.ylabel('frequency')
    plt.title('TEMP HISTOGRAM')
    plt.savefig('tempHistogramMat.png')
    plt.clf() 


def createImageWithLibrarySeaborn(y):
    plot = sb.boxplot(data = y, orient = "h")
    fig = plot.get_figure()
    fig.savefig('humidBoxPlotSea.png')
    fig.clf()



def main():
    data = getData()
    createImageWithLibrarySeaborn(data.getHumidColWithPand())
    createImageWithLibraryMat(data.getTempColWithPand())
    

main()




