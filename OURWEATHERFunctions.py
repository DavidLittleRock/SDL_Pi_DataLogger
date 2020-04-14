
######################################
#
# readOURWEATHERData and buildOURWEATHERGraph
#
#
######################################

import gc
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

DebugOn = False
if DebugOn:
    print(" **************** Debug is ON. ************* ")
try:
    from urlparse import urlparse
except ImportError:
    from urllib.parse import urlparse

from datetime import datetime
import MySQLdb as mdb
import scipy
from scipy import signal

dataBaseName = "DataLogger"
OURWEATHERtableName = 'OURWEATHERTable'

# set up your OurWeather IP Address here
# uri = 'http://192.168.1.135/FullDataString'
uri = 'http://192.168.1.135/DataLoggerDataString'
path = '/'

# fetch the JSON data from the OurWeather device
def fetchJSONData(uri, path):
    target = urlparse(uri+path)
    method = 'GET'
    body = ''

    h = http.Http()
    
    # If you need authentication some example:
    #if auth:
    #    h.add_credentials(auth.user, auth.password)

    response, content = h.request(
            target.geturl(),
            method,
            body,
            headers)

    # assume that content is a json reply
    # parse content with the json module
    data = json.loads(content)  #json.loads converts to a python string

    return data

headers = {
    'Accept': 'application/json',
    'Content-Type': 'application/json; charset=UTF-8'
}


def readOURWEATHERData(username, password):
    print('readOURWEATHERData - The time is: %s' % datetime.now())

    try:
        data = fetchJSONData(uri, path)
    except:
        print ("-----Can't read from OurWeather")
    if DebugOn:
        print("Data from OurWeather= ", data)
    
    # pre split weather data
    preSplitData = data['DataLoggerDataString'] # pull the DataLoggerDataString out of the data string
    if DebugOn:
        print("preSplitData from OutWeather= ", preSplitData)
    WData = preSplitData.split(",") # split on , and put into array WData
    if DebugOn:
        print ("WData from OurWeather= ", WData)

    if (len(WData) < 13):   #change to 13 from 18
        # we have a bad read
        # try again later
        print ("bad read from OurWeather")
        return 0

 #   if (len(WData) == 18):
        # Version does not have air quality
  #      WData.append(0)
  #      WData.append(4)
 
    # open database
    con = mdb.connect('localhost', username, password, dataBaseName )
    cur = con.cursor()

    # Now put the data in MySQL
    # Put record in MySQL

    print ("writing SQLdata ");

    # write record
    deviceid = 0
#     query = 'INSERT INTO '+OURWEATHERtableName+('(timestamp, deviceid, Outdoor_Temperature , Outdoor_Humidity , Indoor_Temperature , Barometric_Pressure , Altitude , Current_Wind_Speed , Current_Wind_Gust , Current_Wind_Direction , Rain_Total , Wind_Speed_Minimum , Wind_Speed_Maximum , Wind_Gust_Minimum , Wind_Gust_Maximum , Wind_Direction_Minimum , Wind_Direction_Maximum , Display_English_Metrice , OurWeather_DateTime , OurWeather_Station_Name , Current_Air_Quality_Sensor , Current_Air_Quality_Qualitative, Battery_Voltage, Battery_Current, Solar_Voltage, Solar_Current, Load_Voltage, Load_Current) VALUES(UTC_TIMESTAMP(),  %i, %.3f, %.3f, %.3f, %.3f, %.3f, %.3f, %.3f, %.3f,%.3f, %.3f, %.3f, %.3f, %.3f, %.3f, %.3f, %i, "%s" , "%s", %i, %i,%.3f,%.3f, %.3f,%.3f,%.3f,%.3f)' % ( int(data['id']), float(WData[0]), float(WData[1]), float(WData[2]),float(WData[3]), float(WData[4]), float(WData[5]), float(WData[6]), float(WData[7]), float(WData[8]), float(WData[9]), float(WData[10]), float(WData[11]), float(WData[12]), float(WData[13]), float(WData[14]), int(WData[15]), WData[16], WData[17], int(WData[18]), int(WData[19]), float(WData[20]), float(WData[21]), float(WData[22]), float(WData[23]), float(WData[24]), float(WData[25])) ) 
    ##    in query below I substract 6 hours fron UTC_TIMESTAMP to convert to central time
    query = 'INSERT INTO '+OURWEATHERtableName+('(timestamp, deviceid, Outdoor_Temperature , Outdoor_Humidity , Barometric_Pressure , \
        Current_Wind_Speed , Current_Wind_Gust , Current_Wind_Direction , Wind_Speed_Maximum , Wind_Gust_Maximum , Display_English_Metric , \
        OurWeather_DateTime , Lightning_Time , Lightning_Distance , Lightning_Count) VALUES(UTC_TIMESTAMP() - INTERVAL 6 HOUR,  \
        %i, %.3f, %.3f, %.3f, %.3f, %.3f, %.3f, %.3f, %.3f, %i, "%s" , "%s", %i, %i)' % ( int(data['id']), float(WData[0]), float(WData[1]),
                                                                                                float(WData[2]), float(WData[3]), float(WData[4]), float(WData[5]),
                                                                                                float(WData[6]), float(WData[7]), int(WData[8]), WData[9],
                                                                                                WData[11], int(WData[12]), int(WData[13]))) 

    print("query=%s" % query)

    cur.execute(query)  
    con.commit()

#
# OURWEATHER graph building routine

def buildOURWEATHERGraphTemperature(username, password, myGraphSampleCount):
        print('buildOURWEATHERGraphTemperature - The time is: %s' % datetime.now())

        # open database
        con1 = mdb.connect('localhost', username, password, dataBaseName )
        # now we have to get the data, stuff it in the graph 
        mycursor = con1.cursor()

        print (myGraphSampleCount)
        query = '(SELECT timestamp, deviceid, Outdoor_Temperature, Outdoor_Humidity, id FROM '+OURWEATHERtableName+' WHERE deviceid=5 ORDER BY id DESC LIMIT '+ str(myGraphSampleCount) + ') ORDER BY id ASC' 

        print ("query= ", query)
        try:
            mycursor.execute(query)
            result = mycursor.fetchall()
        except:
            e=sys.exc_info()[0]
            print ("Error: %s" % e)
        if DebugOn:
            print("Result from SQL= ", result)

        t = []   # time
        u = []   # Outdoor temperature
        v = []   # Outdoor humidity
        averageTemperature = 0.0

        for record in result:
            if DebugOn:
                print("Record in Result= ", record)
            t.append(record[0])
            u.append((record[2] *9/5)+32) # convert the temperature from C to F
            v.append(record[3])
            StationName = record[4]
        aveTemp = mean(u)
        maxTemp = max(u)
        minTemp = min(u)
        print ("count of t=",len(t))
                
        #x = [datetime.strptime(d, '%Y-%m-%d %H:%M:%S',) for d in t]
        x = [d for d in t]
        if DebugOn:
            print("x from t= ", x)
        fds = dates.date2num(x) # convert the datetime object from python to matplotlob time number
        if DebugOn:
            print("fds= ", fds)
        #fds = t # converted
        # matplotlib date format object
        #hfmt = dates.DateFormatter('%H:%M:%S')
        hfmt = dates.DateFormatter('%m/%d-%H')

        fig, ax = pyplot.subplots(figsize=(17.0,8.0), facecolor='green') # make figure(fig) with first subplot axes (ax)
        
        ax.grid(b='True', which='major', axis='both', linestyle='-', color='black')
        pyplot.minorticks_on()
        ax.grid(b='True', which='minor', axis='x', linestyle='-.', color='black')

        ax.xaxis.set_major_formatter(hfmt)
        pyplot.xticks(rotation='45')
        pyplot.subplots_adjust(bottom=0.1, left=0.05) # space from fig edge to axes edge
        
        ax.plot(fds, u, color='red',label="Outside Temp (F) ",linestyle="--",marker=".") # x=fds(the matplotlib date number), y= u(temperature)
        ax.set_xlabel("Time")
        ax.set_ylabel("degrees F")
        ax.legend(loc='upper left')
        ax.axis([max(fds)-7, max(fds), 10, 110])
        if myGraphSampleCount == 288:
            ax.axis([max(fds)-1, max(fds), 10, 110])
        if myGraphSampleCount == 576:
            ax.axis([max(fds)-2, max(fds), 10, 110])
        if myGraphSampleCount == 2016:
            ax.axis([max(fds)-7, max(fds), 10,110])
        
        ax2 = ax.twinx()
        ax2.set_ylabel("% Humidity")
        ax2.plot(fds, v, color='blue',label="Outside Hum %",linestyle="--",marker=".")
        ax2.legend(loc='upper right')
        
        pylab.figtext(0.5, 0.11, ("%s \nAverage Temperature: %6.2f \n %s \n Max Temp: %6.1f Min Temp: %6.1f") %( "WeatherStation", aveTemp, datetime.now(), maxTemp, minTemp),fontsize=10,ha='center',va='bottom')
        pyplot.figtext(0.5, 0.25, ("Temperature = %6.1f") %(u[len(u) - 1]), fontsize=14, ha='center', va='bottom')


        pyplot.show()
        pyplot.savefig("/var/www/html/OURWEATHERDataLoggerGraphTemperature.png", facecolor=fig.get_facecolor()) 

        if myGraphSampleCount == 288:
            
            pyplot.savefig("/var/www/html/OURWEATHERDataLoggerGraphTemperature1.png", facecolor=fig.get_facecolor()) 
        if myGraphSampleCount == 576:
            pyplot.savefig("/var/www/html/OURWEATHERDataLoggerGraphTemperature2.png", facecolor=fig.get_facecolor())
        if myGraphSampleCount == 2016:
            pyplot.savefig("/var/www/html/OURWEATHERDataLoggerGraphTemperature3.png", facecolor=fig.get_facecolor())

        mycursor.close()         
        con1.close()

        fig.clf()
        pyplot.close()
        pylab.close()
        gc.collect()
        print ("------OURWEATHERGraphTemperature finished now")


def buildOURWEATHERGraphWind(username, password, myGraphSampleCount):
        print('buildOURWEATHERWindGraph - The time is: %s' % datetime.now())

        # open database
        con1 = mdb.connect('localhost', username, password, 'DataLogger' )
        # now we have to get the data, stuff it in the graph 

        mycursor = con1.cursor()

        print (myGraphSampleCount)
        query = '(SELECT timestamp, deviceid, Current_Wind_Speed, Current_Wind_Gust, id FROM '+OURWEATHERtableName+' WHERE deviceid=2 ORDER BY id DESC LIMIT '+ str(myGraphSampleCount) + ') ORDER BY id ASC' 

        print ("query=", query)
        try:
            mycursor.execute(query)
            result = mycursor.fetchall()
        except:
            e=sys.exc_info()[0]
            print ("Error: %s" % e)


        t = []   # time
        u = []   # Current Wind Speed
        v = []   # Current Wind Gust 
        averageWindSpeed = 0.0
        currentCount = 0

        for record in result:
            t.append(record[0])
            u.append(record[2]*0.621)
            v.append(record[3]*0.621)
  #          averageWindSpeed = averageWindSpeed+record[2]
   #         currentCount=currentCount+1
   #         StationName = record[4]

        averageWindSpeed = mean(u)
        vSG =[]
        uSG = []
        vSG = signal.savgol_filter(v, 25,5) # apply the Savgo filter to smooth curve
        uSG = signal.savgol_filter(u, 25,5)
        
        print ("count of t=",len(t))
        x = [d for d in t]
        #x = [datetime.strptime(d, '%Y-%m-%d %H:%M:%S',) for d in t]
    
        fds = dates.date2num(x) # converted

        # matplotlib date format object
  #      hfmt = dates.DateFormatter('%H:%M:%S')
        hfmt = dates.DateFormatter('%m/%d-%H')
        fig, ax = pyplot.subplots(figsize=(17.0,8.0), facecolor='red')
  #      fig = pyplot.figure()
#        fig.set_facecolor('white')
 #       ax = fig.add_subplot(111,facecolor = 'white')
 #       ax.vlines(fds, -200.0, 1000.0,colors='w')
        ax.grid(b='True', which='major', axis='both', linestyle='--')


        #ax.xaxis.set_major_locator(dates.MinuteLocator(interval=1))
        ax.xaxis.set_major_formatter(hfmt)
  #      ax.set_ylim(bottom = -200.0)
        pyplot.xticks(rotation='45')
        pyplot.subplots_adjust(bottom=0.1, left=0.05)
        ax.plot(fds, uSG, color='red',label="Wind Speed (mph)" ,linestyle="solid",marker=".")  #u
        ax2=ax.twinx()
        ax2.plot(fds, vSG, color='blue',label="Wind Gust (mph)" ,linestyle="-.",marker=".")
        ax.set_xlabel("Time")
        ax.set_ylabel("Wind (mph)")
        ax.legend(loc='upper left')
        ax2.legend(loc='upper right')
        ax.axis([max(fds)-2, max(fds), 0, max(vSG)+1])
        ax2.axis([max(fds)-2, max(fds), 0, max(vSG)+1])
        pylab.figtext(.5, .5, ("Average Windspeed %6.2f\n%s") %(averageWindSpeed, datetime.now()),fontsize=12,ha='center')

  #      pylab.grid(True)

        pyplot.show()
        pyplot.savefig("/var/www/html/OURWEATHERDataLoggerGraphWind.png", facecolor=fig.get_facecolor())    



        mycursor.close()         
        con1.close()

        fig.clf()
        pyplot.close()
        pylab.close()
        gc.collect()
        print ("------OURWEATHERGraphWind finished now")


 
def buildBarometricPressureGraph(username, password, myGraphSampleCount):
         myGraphSampleCount = 288
         print('buildBarometricPressureGraph - The time is: %s' % datetime.now(timezone('US/Pacific')))
 
         # open database
         con1 = mdb.connect('localhost', username, password, dataBaseName )
         # now we have to get the data, stuff it in the graph 
         mycursor = con1.cursor()
 
         print ("myGraphSampleCount= ", myGraphSampleCount)
         query = '(SELECT timestamp, deviceid, Barometric_Pressure, id FROM '+OURWEATHERtableName+' ORDER BY id DESC LIMIT '+ str(myGraphSampleCount) + ') ORDER BY id ASC' 
         print ("query=", query)
         try:
             mycursor.execute(query)
             result = mycursor.fetchall()
         except:
             e=sys.exc_info()[0]
             print ("Error: %s" % e)
 
         
         t = []   # time
         u = []   # Barometric Pressure 
 
         for record in result:
             t.append(record[0])
             if record[2] is not None:
                 u.append(round((record[2]/3386.4),2))
             elif record[2] is None:
                 u.append(record[2])
 
         print ("count of t=",len(t))
         
         queryMinPres = '(SELECT min(Barometric_Pressure) FROM '+OURWEATHERtableName+')'
         queryMaxPres = '(SELECT max(Barometric_Pressure) FROM '+OURWEATHERtableName+')'

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
         maxPres = (max(maxP)+0.1)
   #      print ("minPressure= ", minPres)
   #      print ("maxPressure= ", maxPres)
         
         
         x1 = [d for d in t]
     
         fds = dates.date2num(x1) # converted
 
         # matplotlib date format object
         #hfmt = dates.DateFormatter('%H:%M:%S')
         hfmt = dates.DateFormatter('%m/%d-%H')
 
         fig = pyplot.figure(figsize=(17.0,8.0), frameon=True, edgecolor='black')
         fig.set_facecolor('white')
         ax = fig.add_subplot(111,facecolor = 'white')
         ax.vlines(fds, -200.0, 1000.0,colors='w')
          
 
         ax.xaxis.set_major_formatter(hfmt)
         pyplot.xticks(rotation='45')
         pyplot.subplots_adjust(bottom=0.1, left=0.05)
         pylab.plot(fds, u, color='red',label="Barrometric Pressure",linestyle="-",marker=".")
         pylab.xlabel("Time")
         pylab.ylabel("Pressure")
         pylab.legend(loc='upper left', fontsize='x-small')

         pylab.axis([max(fds)-2, max(fds), 29.5, 30.5])
 
         pylab.figtext(.5, .5, ("Barometric Pressure = %6.1f\n%s") % (u[len(t)-1],datetime.now(timezone('US/Pacific'))),fontsize=12,ha='center')
         pylab.grid(True)
 
         pyplot.show()
         pyplot.savefig("/var/www/html/OURWEATHERDataLoggerGraphSolarCurrent.png", facecolor=fig.get_facecolor())    
 
 
 
         mycursor.close()         
         con1.close()
 
         fig.clf()
         pyplot.close()
         pylab.close()
         gc.collect()
         print ("------BaromrtricPressureGraph finished now")
# 
#

def findOURWEATHERMaxTemperature(username, password):
        print('buildOURWEATHERGraph - The time is: %s' % datetime.now())

        # open database
        con1 = mdb.connect('localhost', username, password, 'DataLogger' )
        # now we have to get the data, stuff it in the graph 
        mycursor = con1.cursor()

#         print (myGraphSamp)
        query = '(SELECT Outdoor_Temperature FROM '+OURWEATHERtableName+' WHERE DATE(OurWeather_DateTime)= CURRENT_DATE)'
#                   SELECT `Outdoor_Temperature` FROM OURWEATHERTable WHERE DATE(`OurWeather_DateTime`)= CURRENT_DATE

        print ("query=", query)
        try:
            mycursor.execute(query)
            result = mycursor.fetchall()
            print(result)
        except:
            e=sys.exc_info()[0]
            print ("Error: %s" % e)
 

        t = []   # time
   #     u = []   # Current Wind Speed
   #     v = []   # Current Wind Gust 
   #     averageWindSpeed = 0.0
   #     currentCount = 0

        for record in result:
            t.append(record[0])
    #        u.append(record[2])
    #        #v.append(record[3])
    #        averageWindSpeed = averageWindSpeed+record[2]
    #        currentCount=currentCount+1
    #        StationName = record[4]
        maxTemperature=(max(record)*9/5)+32
        print("Max Temperature= ", maxTemperature)
    #    averageWindSpeed = averageWindSpeed/currentCount





def buildMyWeatherGraph(username, password, myGraphSampleCount):
        print('buildMyWeatherGraph - The time is: %s' % datetime.now())

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


        t = []   # Date
        u = []   # Max Temperature
        v = []   # Min Temperature

        for record in result:
            t.append(record[0])
            u.append((record[1] *9/5)+32) # convert the temperature from C to F
            v.append((record[2] *9/5)+32)

        lastReading=len(u)
        print("last reading=" ,lastReading)
        print ("count of t=",len(t))
               
                
        #x = [datetime.strptime(d, '%Y-%m-%d %H:%M:%S',) for d in t]
        
#        x = [d for d in t]
        
  #      fds = dates.date2num(x) # converted  the -0.25 is to subtract 6 hours from UTC to convert to Central Time USA. update did conversion on write not read
        
        #fds = t # converted
        # matplotlib date format object
        #hfmt = dates.DateFormatter('%H:%M:%S')
  #      hfmt = dates.DateFormatter('%m/%d-%H')

        fig, ax = pyplot.subplots(figsize=(17.0,8.0), facecolor='green')
        fig.suptitle("Daily Max and Min Temperature", fontsize=12)
        pylab.figtext(0.5,0.1,"FigText")
        
        ax.grid(b='True', which='major', axis='both', linestyle='--')               

#        ax.xaxis.set_major_formatter(hfmt)
        pyplot.xticks(rotation='45')
#        pyplot.subplots_adjust(bottom=.3, left=0.1)
 #       fig.xticks(rotation='45')
        fig.subplots_adjust(bottom=.1, left=0.1)


        ax.plot(t, u, color='r',label="Max Temp (F) ",linestyle="--",marker=".")
        ax.set_xlabel("Date")
        ax.set_ylabel("degrees F")
        ax.legend(loc='upper left')
        ax.axis([min(t), max(t), 10, 110])
        
        ax2 = ax.twinx()
        ax2.set_ylabel("degrees F")
        ax2.plot(t, v, color='b',label="Min Temp (F)",linestyle="-",marker=".")
        ax2.axis([min(t), max(t), 10, 110])
        ax2.legend(loc='upper right')
#        pylab.figtext(0.5, 0.05, ("%s \nAverage Temperature %6.2f\n%s") %( "WeatherStation", averageTemperature, datetime.now()),fontsize=6,ha='left',va='bottom')
 #       pyplot.figtext(0.5, 0.32, ("Temperature = %6.1f") %(u[lastReading - 1]), fontsize=14, ha='left', va='bottom')
 #       pyplot.figtext(0.5, 0.32, ("Temperature = %6.1f") %(u[myGraphSampleCount - 1]), fontsize=14, ha='left', va='bottom')

#        pylab.grid(True)
#
#
 #       fig.tight_layout()
#
        pyplot.show()
        pyplot.savefig("/var/www/html/MyWeatherGraph.png", facecolor=fig.get_facecolor()) 



        mycursor.close()         
        con1.close()

        fig.clf()
        pyplot.close()
        pylab.close()
        gc.collect()
        print ("------MyWeatherGraph finished now")




def buildRainPerHourGraph(username, password, myGraphSampleCount):
        print('buildRainPerHourGraph - The time is: %s' % datetime.now())
  #      print('buildOURWEATHERGraphTemperature - The time is: %s' % datetime.now())

        # open database
        con1 = mdb.connect('localhost', username, password, dataBaseName )
        # now we have to get the data, stuff it in the graph 
        mycursor = con1.cursor()

        print (myGraphSampleCount)
        query = '(SELECT timestamp, deviceid, Rain_Total, Rain_Now, id FROM '+OURWEATHERtableName+' WHERE deviceid=2 ORDER BY id DESC LIMIT '+ str(myGraphSampleCount) + ') ORDER BY id ASC' 

        print ("query= ", query)
        try:
            mycursor.execute(query)
            result = mycursor.fetchall()
        except:
            e=sys.exc_info()[0]
            print ("Error: %s" % e)
        if DebugOn:
            print("Result from SQL= ", result)

        t = []   # time
        u = []   # Outdoor temperature
        v = []   # Outdoor humidity
        averageTemperature = 0.0
#       currentCount = 0

        for record in result:
            if DebugOn:
                print("Record in Result= ", record)
            t.append(record[0])
            u.append(record[2]) # convert the temperature from C to F
            v.append(record[3])
            StationName = record[4]
  #      aveTemp = mean(u)
  #      maxTemp = max(u)
  #      minTemp = min(u)
#        lastReading=len(u)
#        print("last reading=" ,lastReading)
        print ("count of t=",len(t))
                
        #x = [datetime.strptime(d, '%Y-%m-%d %H:%M:%S',) for d in t]
        x = [d for d in t]
        if DebugOn:
            print("x from t= ", x)
        fds = dates.date2num(x) # convert the datetime object from python to matplotlob time number
        if DebugOn:
            print("fds= ", fds)
        #fds = t # converted
        # matplotlib date format object
        #hfmt = dates.DateFormatter('%H:%M:%S')
        hfmt = dates.DateFormatter('%m/%d-%H')

        fig, ax = pyplot.subplots(figsize=(17.0,8.0), facecolor='green') # make figure(fig) with first subplot axes (ax)
        
        ax.grid(b='True', which='major', axis='both', linestyle='-', color='black')
        pyplot.minorticks_on()
        ax.grid(b='True', which='minor', axis='x', linestyle='-.', color='black')

        ax.xaxis.set_major_formatter(hfmt)
        pyplot.xticks(rotation='45')
        pyplot.subplots_adjust(bottom=0.1, left=0.05) # space from fig edge to axes edge
        
        ax.plot(fds, u, color='red',label="Outside Temp (F) ",linestyle="--",marker=".") # x=fds(the matplotlib date number), y= u(temperature)
        ax.set_xlabel("Time")
        ax.set_ylabel("degrees F")
        ax.legend(loc='upper left')
        ax.axis([min(fds), max(fds), 0, max(u)+1])
        
#        ax2 = pylab.twinx()
        ax2 = ax.twinx()
        ax2.set_ylabel("% Humidity")
        ax2.plot(fds, v, color='blue',label="Outside Hum %",linestyle="--",marker=".")
        ax2.legend(loc='upper right')
        ax2.axis([min(fds), max(fds), 0, max(u)+1])
       
#        pylab.figtext(0.5, 0.11, ("%s \nAverage Temperature: %6.2f \n %s \n Max Temp: %6.1f Min Temp: %6.1f") %( "WeatherStation", aveTemp, datetime.now(), maxTemp, minTemp),fontsize=6,ha='center',va='bottom')
#        pyplot.figtext(0.5, 0.25, ("Temperature = %6.1f") %(u[len(u) - 1]), fontsize=14, ha='center', va='bottom')
 #       pyplot.figtext(0.5, 0.32, ("Temperature = %6.1f") %(u[myGraphSampleCount - 1]), fontsize=14, ha='left', va='bottom')

#        pylab.grid(True)
#
#
 #       fig.tight_layout()
        pyplot.show()
        pyplot.savefig("/var/www/html/RainPerHourGraph.png", facecolor=fig.get_facecolor()) 



        mycursor.close()         
        con1.close()

        fig.clf()
        pyplot.close()
        pylab.close()
        gc.collect()
        print ("------RainPerHourGraph finished now")
        
        


def buildTemperatureAndHumidityGraph(username, password, myGraphSampleCount):
        print('buildTemperatureAndHumidityGraph - The time is: %s' % datetime.now())

        # open database
        con1 = mdb.connect('localhost', username, password, dataBaseName )
        # now we have to get the data, stuff it in the graph 
        mycursor = con1.cursor()
        deviceid = 6
#        print (myGraphSampleCount)
        query = '(SELECT timestamp, deviceid, Outdoor_Temperature, Outdoor_Humidity, id FROM '+OURWEATHERtableName+' WHERE deviceid=5 ORDER BY id DESC LIMIT '+ str(myGraphSampleCount) + ') ORDER BY id ASC' 

        print ("query= ", query)
        try:
            mycursor.execute(query)
            result = mycursor.fetchall()
        except:
            e=sys.exc_info()[0]
            print ("Error: %s" % e)
        
#        print("Result from SQL= ", result)

        

        t = []   # time
        u = []   # Outdoor temperature
        v = []   # Outdoor humidity
        averageTemperature = 0.0

        for record in result:
            if DebugOn:
                print("Record in Result= ", record)
            t.append(record[0])
            u.append((record[2] *9/5)+32) # convert the temperature from C to F
            v.append(record[3])
            StationName = record[4]
        aveTemp = mean(u)
        maxTemp = max(u)
        minTemp = min(u)
        print ("count of t=",len(t))
                
        #
                
        #x = [datetime.strptime(d, '%Y-%m-%d %H:%M:%S',) for d in t]
        x = [d for d in t]
        if DebugOn:
            print("x from t= ", x)
        fds = dates.date2num(x) # convert the datetime object from python to matplotlob time number
        if DebugOn:
            print("fds= ", fds)
        #fds = t # converted
        # matplotlib date format object
        #hfmt = dates.DateFormatter('%H:%M:%S')
        hfmt = dates.DateFormatter('%m/%d-%H')

        fig, ax = pyplot.subplots(figsize=(17.0,8.0), facecolor='green') # make figure(fig) with first subplot axes (ax)
        
        ax.grid(b='True', which='major', axis='both', linestyle='-', color='black')
        pyplot.minorticks_on()
        ax.grid(b='True', which='minor', axis='x', linestyle='-.', color='black')

        ax.xaxis.set_major_formatter(hfmt)
        pyplot.xticks(rotation='45')
        pyplot.subplots_adjust(bottom=0.1, left=0.05) # space from fig edge to axes edge
        
        ax.plot(fds, u, color='red',label="Outside Temp (F) ",linestyle="--",marker=".") # x=fds(the matplotlib date number), y= u(temperature)
        ax.set_xlabel("Time")
        ax.set_ylabel("degrees F")
        ax.legend(loc='upper left')
        ax.axis([max(fds)-7, max(fds), 10, 110])
        if myGraphSampleCount == 288:
            ax.axis([max(fds)-1, max(fds), 10, 110])
        if myGraphSampleCount == 576:
            ax.axis([max(fds)-2, max(fds), 10, 110])
        if myGraphSampleCount == 2016:
            ax.axis([max(fds)-7, max(fds), 10,110])
        
        ax2 = ax.twinx()
        ax2.set_ylabel("% Humidity")
        ax2.plot(fds, v, color='blue',label="Outside Hum %",linestyle="--",marker=".")
        ax2.legend(loc='upper right')
        
        pylab.figtext(0.5, 0.11, ("%s \nAverage Temperature: %6.2f \n %s \n Max Temp: %6.1f Min Temp: %6.1f") %( "WeatherStation", aveTemp, datetime.now(), maxTemp, minTemp),fontsize=10,ha='center',va='bottom')
        pyplot.figtext(0.5, 0.25, ("Temperature = %6.1f") %(u[len(u) - 1]), fontsize=14, ha='center', va='bottom')


        pyplot.show()
        pyplot.savefig("/var/www/html/TemperatureAndHumidityGraph.png", facecolor=fig.get_facecolor()) 

        if myGraphSampleCount == 288:
            
            pyplot.savefig("/var/www/html/TemperatureAndHumidityGraph1.png", facecolor=fig.get_facecolor()) 
        if myGraphSampleCount == 576:
            pyplot.savefig("/var/www/html/TemperatureAndHumidityGraph2.png", facecolor=fig.get_facecolor())
        if myGraphSampleCount == 2016:
            pyplot.savefig("/var/www/html/TemperatureAndHumidityGraph3.png", facecolor=fig.get_facecolor())

        mycursor.close()         
        con1.close()

        fig.clf()
        pyplot.close()
        pylab.close()
        gc.collect()
        print ("------TemperatureAndHumidityGraph finished now ------")        
