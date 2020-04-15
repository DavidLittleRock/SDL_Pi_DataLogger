
import gc  #python garbage collector
import matplotlib
# Force matplotlib to not use any Xwindows backend.
matplotlib.use('Agg')

from matplotlib import pyplot
from matplotlib import dates
from matplotlib.ticker import MultipleLocator, FormatStrFormatter
import pylab
from numpy import mean
import sys

from pytz import timezone
import httplib2 as http
import json

from datetime import datetime
import MySQLdb as mdb
import scipy
from scipy import signal


dataBaseName = "DataLogger"
dataBaseTable = 'OURWEATHERTable'
#mysql user
username = "datalogger"
#mysql Password
password = 'Data0233'

def print_ts(txt = 'Variable ', msg = None):  # print with a time stamp
    dz = datetime.strftime(datetime.now(), '%H:%M, %A')
    print ("-"*100)
    if msg is not None:
        print ("[{date}] {text} ==is =={message}".format(date = dz, text = txt, message = msg))
    else:
        print ("[{date}] {text} ".format(date = dz, text = txt))
    print ("-"*100)

def buildTemperatureAndHumidityGraph(username, password, myGraphSampleCount):
    thisDate = datetime.now()

    print_ts(txt = 'buildTemperatureAndHumidityGraph - The time is: {}'.format(datetime.now()))
    # open database
    con1 = mdb.connect('localhost', username, password, dataBaseName) #('localhost', username, password, dataBaseName )
    # now we have to get the data, stuff it in the graph 
    mycursor = con1.cursor()
#        print (myGraphSampleCount)

    daysToPrint = [1,2,7]
    for days in daysToPrint:
        query = '(SELECT timestamp, deviceid, Outdoor_Temperature, Outdoor_Humidity, id FROM '+dataBaseTable+' WHERE DATE(timestamp)>=Current_Date - '+str(days)+' LIMIT '+ str(myGraphSampleCount) + ') ORDER BY id ASC' 
    
        try:
            mycursor.execute(query)
            result = mycursor.fetchall()
        except:
            e=sys.exc_info()[0]
            print ("Error: {}".format(e))

        time = []   # time
        temperature = []   # Outdoor temperature
        humidity = []   # Outdoor humidity

        for record in result:
            time.append(record[0])
            temperature.append((record[2] *9/5)+32) # convert the temperature from C to F
            humidity.append(record[3])
        aveTemp = mean(temperature)
        maxTemp = max(temperature)
        minTemp = min(temperature)

        fds = [dates.date2num(d) for d in time] # time is a list of datetime.datetime objects and this converts to a float representintation
        
        hfmt = dates.DateFormatter('%m/%d-%H')
                    
        fig, ax = pyplot.subplots(figsize=(17.0,8.0), facecolor='green') # make figure(fig) with first subplot axes (ax)
        fig.suptitle('Temperature and Humidity, {} days'.format(days), fontsize=12)
        
        pyplot.xticks(rotation='45')
        pyplot.subplots_adjust(bottom=0.1, left=0.05) # space from fig edge to axes edge
        pyplot.figtext(0.8, 0.9, ('Average Temperature: {:6.2f} \n {} \n Max Temp: {:6.1f} Min Temp: {:6.1f}').format(aveTemp, datetime.strftime(thisDate, '%c'), maxTemp, minTemp),fontsize=10,ha='left',va='bottom')
        pyplot.figtext(0.1, 0.9, ('Temperature now = {:6.1f}').format(temperature[len(temperature) - 1]), fontsize=14, ha='left', va='bottom')
        
        ax.grid(b='True', which='major', axis='both', linestyle='-', linewidth=2, color='black')
        ax.grid(b='True', which='major', axis='y',linewidth=1)

        ax.grid(b='True', which='minor', axis='x', linestyle='-.', color='black')
        ax.xaxis.set_major_formatter(hfmt)
        ax.xaxis.set_minor_locator(dates.HourLocator(interval=1))
        ax.xaxis.set_minor_locator(dates.HourLocator(byhour=(6,12,18)))

        ax.plot(fds, temperature, color='red',label="Outside Temp (F) ",linestyle="--",marker=".") # x=fds(the matplotlib date number), y= u(temperature)
        ax.set_xlabel("Time")
        ax.set_ylabel("degrees F")
        ax.legend(loc='upper left')
        ax.axis([dates.date2num(datetime.now())-days, dates.date2num(datetime.now()), 10, 110])

#             ax = makeAx(ax, hfmt, fds, temperature, days)

        ax2 = ax.twinx()
        ax2.set_ylabel("% Humidity")
        ax2.plot(fds, humidity, color='blue',label="Outside Hum %",linestyle="--",marker=".")
        ax2.legend(loc='upper right')
        ax2.axis([dates.date2num(datetime.now())-days, dates.date2num(datetime.now()), 10, 110])
        
        pyplot.savefig('/var/www/html/TemperatureAndHumidityGraph'+str(days)+'.png', facecolor=fig.get_facecolor()) 

    pyplot.show()
    mycursor.close()         
    con1.close()
    fig.clf()
    pyplot.close()
    gc.collect()
    print_ts (txt = '------TemperatureAndHumidityGraph finished now ------')
        
        
def buildWindGraph(username, password, myGraphSampleCount):
    dz = datetime.now()
    print_ts(txt = 'buildWindGraph - The time is: {}'.format(datetime.now()))
    # open database
    con1 = mdb.connect('localhost', username, password, dataBaseName )
    # now we have to get the data, stuff it in the graph 
    mycursor = con1.cursor()
    query = '(SELECT timestamp, deviceid, Current_Wind_Speed, Current_Wind_Gust, id FROM '+dataBaseTable+' WHERE DATE(timestamp) >= Current_Date - 7 LIMIT '+ str(myGraphSampleCount) + ') ORDER BY id ASC'  
    try:
        mycursor.execute(query)
        result = mycursor.fetchall()
    except:
        e=sys.exc_info()[0]
        print ("Error: %s" % e)

    time = []   # time
    windSpeed = []   # Current Wind Speed
    gust = []   # Current Wind Gust 

    for record in result:
        time.append(record[0])
        windSpeed.append(record[2] * 0.621) #convert kph to mph
        gust.append(record[3] * 0.621)
    averageWindSpeed = mean(windSpeed)
    windSpeedSG =[]
    gustSG = []
    windSpeedSG = signal.savgol_filter(windSpeed, 25, 5) # apply the Savgo filter to smooth curve
    gustSG = signal.savgol_filter(gust, 25, 5)
    #x = [datetime.strptime(d, '%Y-%m-%d %H:%M:%S',) for d in t]
    fds = [dates.date2num(d) for d in time] # converted

    hfmt = dates.DateFormatter('%m/%d-%H')
    fig, ax = pyplot.subplots(figsize=(17.0,8.0), facecolor='red')
    fig.suptitle('Wind and Gust', fontsize=12)

    ax.grid(b='True', which='major', axis='both', linestyle='--')
    ax.xaxis.set_major_formatter(hfmt)
    pyplot.xticks(rotation='45')
    pyplot.subplots_adjust(bottom=0.1, left=0.05)
    ax.plot(fds, windSpeedSG, color='red',label='Wind Speed (mph)' ,linestyle='solid',marker=".")  #u
    ax2=ax.twinx()
    ax2.plot(fds, gustSG, color='blue',label='Wind Gust (mph)' ,linestyle='-.',marker='.')
    ax.set_xlabel('Time')
    ax.set_ylabel('Wind (mph)')
    ax.legend(loc='upper left')
    ax2.legend(loc='upper right')
    ax.axis([dates.date2num(datetime.now())-2, dates.date2num(datetime.now()), 0, max(gustSG)+1])
    ax2.axis([dates.date2num(datetime.now())-2, dates.date2num(datetime.now()), 0, max(gustSG)+1])

    pyplot.figtext(0.9, 0.9, ('Average Windspeed {AveWind:6.2f}\n{time}').format(AveWind=averageWindSpeed, time=datetime.strftime(dz, '%c')),fontsize=12,ha='center')

    pyplot.show()
    pyplot.savefig("/var/www/html/WindAndGustGraph.png", facecolor=fig.get_facecolor())    

    mycursor.close()         
    con1.close()

    fig.clf()
    pyplot.close()
    pylab.close()
    gc.collect()
    print ("------buildWindGraph finished now ------------")




def buildBarometricPressureGraph(username, password, myGraphSampleCount):
         dz = datetime.now()
         print('buildBarometricPressureGraph - The time is: %s' % datetime.strftime(dz, '%H:%M, %A'))
         # open database
         con1 = mdb.connect('localhost', username, password, dataBaseName )
         # now we have to get the data, stuff it in the graph 
         mycursor = con1.cursor()
 
         print ("myGraphSampleCount= ", myGraphSampleCount)
         query = '(SELECT timestamp, deviceid, Barometric_Pressure, id FROM '+dataBaseTable+' WHERE DATE(timestamp) >= Current_Date - 7 LIMIT '+ str(myGraphSampleCount) + ') ORDER BY id ASC' 
#          query = '(SELECT timestamp, deviceid, Barometric_Pressure, id FROM '+dataBaseTable+' ORDER BY id DESC LIMIT '+ str(myGraphSampleCount) + ') ORDER BY id ASC' 
         print ("query=", query)
         try:
             mycursor.execute(query)
             result = mycursor.fetchall()
         except:
             e=sys.exc_info()[0]
             print ("Error: %s" % e)
         
         time = []   # time
         barometricPressure = []   # Barometric Pressure 
 
         for record in result:
             time.append(record[0])
             if record[2] is not None:
                 barometricPressure.append(round((record[2]/3386.4),2))
             elif record[2] is None:
                 barometricPressure.append(record[2])
 
         print ("count of time=",len(time))
         
         queryMinPres = '(SELECT min(Barometric_Pressure) FROM '+dataBaseTable+' )'
         queryMaxPres = '(SELECT max(Barometric_Pressure) FROM '+dataBaseTable+' )'

         try:
             mycursor.execute(queryMinPres)
             resultMinPres = mycursor.fetchall()
         except:
             e=sys.exc_info()[0]
             print ("Error: %s" % e)
         try:
             mycursor.execute(queryMaxPres)
             resultMaxPres = mycursor.fetchall()
         except:
             e=sys.exc_info()[0]
             print ("Error: %s" % e)
         
         minP =[]
         for record in resultMinPres:
             minP.append(round((record[0]/3386.4),2))
         maxP =[]
         for record in resultMaxPres:
             maxP.append(round((record[0]/3386.4),2))
         minPres = min(minP)
         if minPres < 29:
             minPres = 29.1
         maxPres = (max(maxP)+0.01)         
         
         x1 = [d for d in time]
         fds = dates.date2num(x1) # converted
         # matplotlib date format object
         #hfmt = dates.DateFormatter('%H:%M:%S')
         hfmt = dates.DateFormatter('%m/%d-%H')
         fig, ax = pyplot.subplots(figsize=(17.0,8.0), facecolor='blue')
         fig.suptitle('Barometric Pressure Graph', fontsize=12)

         ax.grid(b='True', which='major', axis='both', linestyle='-', color='black')          
 
         ax.xaxis.set_major_formatter(hfmt)
         pyplot.xticks(rotation='45')
         pyplot.subplots_adjust(bottom=0.1, left=0.05)
         ax.plot(fds, barometricPressure, color='red',label="Barrometric Pressure",linestyle="-",marker=".")

         ax.set_xlabel("Time")
         ax.set_ylabel("Pressure")
         ax.legend(loc='upper left', fontsize='x-small')

         ax.axis([dates.date2num(datetime.now())-7, dates.date2num(datetime.now()), minPres, maxPres])
 
         pyplot.figtext(0.9, 0.9, ("Barometric Pressure = {press:6.1f}\n{time}").format(press=barometricPressure[len(time)-1],time=datetime.strftime(dz, '%c')),fontsize=12,ha='center')
         ax.grid(True)
 
         pyplot.show()
         pyplot.savefig("/var/www/html/barometricPressureGraph.png", facecolor=fig.get_facecolor())    
 
         mycursor.close()         
         con1.close()
 
         fig.clf()
         pyplot.close()
         pylab.close()
         gc.collect()
         print ("------baromrtricPressureGraph finished now-----------------")
# 
#

def buildMaxMinTemperatureGraph(username, password, myGraphSampleCount):
        dz = datetime.now()
        print('buildMaxMinTemperatureGraph - The time is: %s' % datetime.strftime(dz, '%H:%M, %A'))

        # open database
        con1 = mdb.connect('localhost', username, password, dataBaseName )
        # now we have to get the data, stuff it in the graph 
        mycursor = con1.cursor()
        print (myGraphSampleCount)
        query = '(SELECT Date, Max, Min FROM MinMaxTemp ) ' # ORDER BY Date  LIMIT 12

        print ("query=", query)
        try:
            mycursor.execute(query)
            result = mycursor.fetchall()
        except:
            e=sys.exc_info()[0]
            print ("Error: %s" % e)

        time = []   # Date
        maxTemperature = []   # Max Temperature
        minTemperature = []   # Min Temperature

        for record in result:
            time.append(record[0])
            maxTemperature.append((record[1] *9/5)+32) # convert the temperature from C to F
            minTemperature.append((record[2] *9/5)+32)

        lastReading=len(maxTemperature)
        print("last reading=" ,lastReading)
        print ("count of t=",len(time))        

        fig, ax = pyplot.subplots(figsize=(17.0,8.0), facecolor='green')
        fig.suptitle("Daily Max and Min Temperature", fontsize=12)
        
        ax.grid(b='True', which='major', axis='both', linestyle='--')
#        ax.xaxis.set_major_formatter(hfmt)
        pyplot.xticks(rotation='45')
#        pyplot.subplots_adjust(bottom=.3, left=0.1)
#        fig.xticks(rotation='45')
        fig.subplots_adjust(bottom=.1, left=0.1)
        ax.plot(time, maxTemperature, color='r',label="Max Temp (F) ",linestyle="--",marker=".")
        ax.set_xlabel("Date")
        ax.set_ylabel("degrees F")
        ax.legend(loc='upper left')
        ax.axis([dates.date2num(datetime.now())-30, dates.date2num(datetime.now()), 10, 110])
        
        ax2 = ax.twinx()
        ax2.set_ylabel("degrees F")
        ax2.plot(time, minTemperature, color='b',label="Min Temp (F)",linestyle="-",marker=".")
        ax2.axis([dates.date2num(datetime.now())-30, dates.date2num(datetime.now()), 10, 110])
        ax2.legend(loc='upper right')
        pyplot.show()
        pyplot.savefig("/var/www/html/MaxMinTemperatureGraph.png", facecolor=fig.get_facecolor()) 

        mycursor.close()         
        con1.close()

        fig.clf()
        pyplot.close()
        pylab.close()
        gc.collect()
        print ("------MaxMinTemperatureGraph finished now")


def yesterdayTemperature():
          # open database
        con1 = mdb.connect('localhost', username, password, dataBaseName )
        # now we have to get the data, stuff it in the graph 
        mycursor = con1.cursor()
        query = '(SELECT Date, Max, Min FROM MinMaxTemp WHERE Date =  Current_Date - 1) ' # ORDER BY Date  LIMIT 12

        print ("query=", query)
        try:
            mycursor.execute(query)
            result = mycursor.fetchall()
        except:
            e=sys.exc_info()[0]
            print ("Error: %s" % e)

        print (result)
        print (result[0][1])
  
  
def makeAx(ax, hfmt, x, y, days):
    ax.grid(b='True', which='major', axis='both', linestyle='-', linewidth=2, color='black')
    ax.grid(b='True', which='major', axis='y', linewidth=1)

    ax.grid(b='True', which='minor', axis='x', linestyle='-.', color='black')
    ax.xaxis.set_major_formatter(hfmt)
    ax.xaxis.set_minor_locator(dates.HourLocator(interval=1))
    ax.xaxis.set_minor_locator(dates.HourLocator(byhour=(6,12,18)))

    ax.plot(x, y, color='red',label="Outside Temp (F) makeAx ",linestyle="--",marker=".") # x=fds(the matplotlib date number), y= u(temperature)
    ax.set_xlabel("Time")
    ax.set_ylabel("degrees F")
    ax.legend(loc='upper left')
    ax.axis([max(x)-days, max(x), 10, 110])
    return ax
  
        
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
        resultA = []
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

            resultA += result



            for record in resultA:
                time.append(record[1])
                rainPeriod.append(record[2]/22.5) 
                rainTotal.append(sum(rainPeriod))
            print ("count of time=",len(time))
#            if len(timeA) != 0:
#                time += timeA
#                rainPeriod += rainPeriodA
#                rainTotal += rainTotalA
        #x = [datetime.strptime(d, '%Y-%m-%d %H:%M:%S',) for d in t]
        x = [d for d in time]        
        fds = dates.date2num(x) # convert the datetime object from python to matplotlob time number
        hfmt = dates.DateFormatter('%m/%d-%H')
                    
        fig, ax = pyplot.subplots(figsize=(17.0,8.0), facecolor='green') # make figure(fig) with first subplot axes (ax)
        fig.suptitle('Rain each day.', fontsize=12)
        
        pyplot.xticks(rotation='45')
        pyplot.subplots_adjust(bottom=0.1, left=0.05) # space from fig edge to axes edge
     
        ax.grid(b='True', which='major', axis='both', linestyle='-', linewidth=2, color='black')
        ax.grid(b='True', which='major', axis='y',linewidth=1)

        ax.grid(b='True', which='minor', axis='x', linestyle='-.', color='black')
        ax.xaxis.set_major_formatter(hfmt)
        ax.xaxis.set_major_locator(dates.DayLocator(interval=1))
        ax.xaxis.set_minor_locator(dates.HourLocator(byhour=(6,12,18)))
        ax.plot(fds, rainPeriod, color='red',label="Rain this period ",linestyle="--",marker=".") # x=fds(the matplotlib date number), y= u(temperature)
        ax.set_xlabel("Time")
        ax.set_ylabel("rain (inch)")
        ax.legend(loc='upper left')
        ax.axis([dates.date2num(datetime.now())-6, dates.date2num(datetime.now()), 0, max(rainTotal)+0.1])
 #       ax.axis([min(fds), max(fds), 0, max(rainTotal)+0.1])


        ax2 = ax.twinx()
        ax2.set_ylabel('Rain Total')
        ax2.plot(fds, rainTotal, color='blue',label="Rain this day", marker='.', linestyle='None')
        ax2.legend(loc='upper right')
        ax2.axis([dates.date2num(datetime.now())-6, dates.date2num(datetime.now()), 0, 0.5])
        
        pyplot.savefig('/var/www/html/RainGraph.png', facecolor=fig.get_facecolor()) 

        pyplot.show()
       
        mycursor.close()         
        con1.close()

        fig.clf()
        pyplot.close()
        gc.collect()
        print ("------RainGraph finished now ------")
        
        
                
 