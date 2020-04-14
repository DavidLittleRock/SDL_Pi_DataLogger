
import gc  #python garbage collector
import matplotlib
# Force matplotlib to not use any Xwindows backend.
matplotlib.use('Agg')

from matplotlib import pyplot
from matplotlib import dates
from matplotlib.ticker import MultipleLocator, FormatStrFormatter
#import pylab
#from numpy import mean
import sys

from pytz import timezone
import httplib2 as http
import json

from datetime import datetime
import MySQLdb as mdb
import scipy
from scipy import signal

# import paho.mqtt.subscribe as subscribe
import paho.mqtt.client as mqtt
#import json
#import OURWEATHERFunctions
import GraphOutput
import SendEmail
#import MQTTClient
import time

broker_url = "192.168.1.201"
broker_port = 1883
dataBaseName = "DataLogger"
dataBaseTable = 'OURWEATHERTable'
username = "datalogger" #mysql user
password = "Data0233"  #mysql
hostName = "localhost"


myGraphSampleCount = 2000

def print_ts(txt = 'Variable ', msg = None):  # print with a time stamp
    dz = datetime.strftime(datetime.now(), '%H:%M, %A')
    print ("-"*100)
    if msg is not None:
        print ("[{}] {} ==is =={}".format(dz, txt, msg))
    else:
        print ("[{}] {} ".format(dz, txt))
    print ("-"*100)

def buildRainGraph(username, password, myGraphSampleCount):
        thisDate = datetime.now()

        print('buildRainGraph - The time is: %s' % datetime.now())
        # open database
        con1 = mdb.connect('localhost', username, password, dataBaseName) #('localhost', username, password, dataBaseName )
        # now we have to get the data, stuff it in the graph 
        mycursor = con1.cursor()
#        print (myGraphSampleCount)
        time = []   # time
        rainPeriod = []   # Outdoor temperature
        rainTotal = []   # Outdoor humidity
        
        daysToPrint = [0,1,2,3,4,5,6,7]
        for days in daysToPrint:
            
            timeA = []
            rainPeriodA = []
            rainTotalA = []
            
            query = '(SELECT id, OurWeather_DateTime, Rain_Change FROM Rain_For WHERE DATE(OurWeather_DateTime)=Current_Date-'+str(days)+' LIMIT '+ str(myGraphSampleCount) + ') ORDER BY id ASC' 
        
            try:
                mycursor.execute(query)
                result = mycursor.fetchall()
            except:
                e=sys.exc_info()[0]
                print ("Error: %s" % e)

            for record in result:
                timeA.append(record[1])
                rainPeriodA.append(record[2]/22.5) # convert the temperature from C to F
                rainTotalA.append(sum(rainPeriodA))
            print ("count of timeA=",len(timeA))
            if len(timeA) != 0:
                time += timeA
                rainPeriod += rainPeriodA
                rainTotal += rainTotalA
        #x = [datetime.strptime(d, '%Y-%m-%d %H:%M:%S',) for d in t]
        x = [d for d in time]        
        fds = dates.date2num(x) # convert the datetime object from python to matplotlob time number
        hfmt = dates.DateFormatter('%m/%d-%H')
                    
        fig, ax = pyplot.subplots(figsize=(17.0,8.0), facecolor='green') # make figure(fig) with first subplot axes (ax)
        fig.suptitle('Rain each day.', fontsize=12)
        
        pyplot.xticks(rotation='45')
        pyplot.subplots_adjust(bottom=0.1, left=0.05) # space from fig edge to axes edge
#             pyplot.figtext(0.8, 0.9, ('Average Temperature: {:6.2f} \n {} \n Max Temp: {:6.1f} Min Temp: {:6.1f}').format(aveTemp, datetime.strftime(thisDate, '%c'), maxTemp, minTemp),fontsize=10,ha='left',va='bottom')
#             pyplot.figtext(0.1, 0.9, ('Temperature now = {:6.1f}').format(temperature[len(temperature) - 1]), fontsize=14, ha='left', va='bottom')
        
        ax.grid(b='True', which='major', axis='both', linestyle='-', linewidth=2, color='black')
        ax.grid(b='True', which='major', axis='y',linewidth=1)

        ax.grid(b='True', which='minor', axis='x', linestyle='-.', color='black')
        ax.xaxis.set_major_formatter(hfmt)
        ax.xaxis.set_major_locator(dates.DayLocator(interval=1))
   #     ax.xaxis.set_minor_formatter(hfmt)
        ax.xaxis.set_minor_locator(dates.HourLocator(byhour=(6,12,18)))
        ax.plot(fds, rainPeriod, color='red',label="Rain this period ",linestyle="--",marker=".") # x=fds(the matplotlib date number), y= u(temperature)
        ax.set_xlabel("Time")
        ax.set_ylabel("rain (inch)")
        ax.legend(loc='upper left')
        ax.axis([min(fds), max(fds), 0, max(rainTotal)+0.1])

        ax2 = ax.twinx()
        ax2.set_ylabel('Rain Total')
        ax2.plot(fds, rainTotal, color='blue',label="Rain this day", marker='.', linestyle='None')
        ax2.legend(loc='upper right')
        ax2.axis([max(fds)- days, max(fds), 0, max(rainTotal)+0.1])
        
        pyplot.savefig('/var/www/html/RainGraph.png', facecolor=fig.get_facecolor()) 

        pyplot.show()
       
        mycursor.close()         
        con1.close()

        fig.clf()
        pyplot.close()
 #       pylab.close()
        gc.collect()
        print ("------RainGraph finished now ------")
        
                
                
                

def main():
#     print_ts ("start main")
#    MQTTClient()
#     print_ts ("main")
 
#     print_ts("command")
#    GraphOutput.yesterdayTemperature()
#    while True:
    try:
        time.sleep(3)
        buildRainGraph(username, password, myGraphSampleCount)
    except Exception, e:
        print(e)
        print("done")


if __name__ == '__main__':
    main()