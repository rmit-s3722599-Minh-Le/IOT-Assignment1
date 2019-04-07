#!/usr/bin/env python3
#import
import pandas as pd
import sqlite3
import os
import matplotlib as mpl
if os.environ.get('DISPLAY','') == '':
    print('no display found. Using non-interactive Agg backend')
    mpl.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sb
import time


#gets the data from the database (humid array and temp array)
class getData():
    def __init__(self):
        self.dbName = 'THS.db'
        self.conn = sqlite3.connect(self.dbName)
        self.curs = self.conn.cursor()

    #gets the db temp column and converts to a data format   
    def getTempColWithPand(self):
        df = pd.read_sql_query("SELECT temp FROM TEMP_HUMID_data", self.conn)
        return df
    #gets the db humid column and converts to a data format  
    def getHumidColWithPand(self):
        
        df = pd.read_sql_query("SELECT humid FROM TEMP_HUMID_data", self.conn)
        return df

#histogram creating of temperatures using mat
def createImageWithLibraryMat(x):
    temp = x['temp']
    #scaling the x axis
    bins = [10,12,14,16,18,20,22,24,26,28,30,32,34,36,38,40,42,44,46,48,50]
    #a bar type histogram with the width of 0.8
    plt.hist(temp, bins, histtype = 'bar', rwidth=0.8)
    #label of x and y axis
    plt.xlabel('temp')
    plt.ylabel('frequency')
    #title of the plot
    plt.title('TEMP HISTOGRAM')
    #saves the plot as a png file: 'tempHistogramMat.png'
    plt.savefig('tempHistogramMat.png')
    #closes file
    plt.clf() 

#box-plot creating of humidities isng seaborn
def createImageWithLibrarySeaborn(y):
    #boxplot contains humidity value and of type horizontal format
    plot = sb.boxplot(data = y, orient = "h")
    #gets the figure of the box plot
    fig = plot.get_figure()
    #saves the plot has a png file: 'humidBoxPlotSea.png'
    fig.savefig('humidBoxPlotSea.png')
    #closes file
    fig.clf()


#main function
def main():
    data = getData()
    createImageWithLibrarySeaborn(data.getHumidColWithPand())
    createImageWithLibraryMat(data.getTempColWithPand())
    
#execute
main()




