#!/usr/bin/env python
# Datalogger.py
# Gather Data, put in SQL, Graph with MatPlot Lib 
# SwitchDoc Labs
# 05/31/2016
# Version 3.0  March 25, 2018
#
# supports:
# CSVSensor
# INA3221 - 3 Channel Current / Voltage Measurement Device
# ADS1115 - 4 Channel 16bit ADC
# OURWEATHER - OurWeather Complete Weather Kit 
# Three Panel Test - 3 Solar Cells and 3 SunAirPlus boards 
# WXLink from SwitchDoc Labs


# configuration variables
# set to true if present, false if not

INA219_Present = False
INA3221_Present = False
ADS1115_Present = False
OURWEATHER_Present = False
ThreePanelTest_Present = False
WXLINK_Present = False
PubNub_Present = True
DebugOn = True
# imports

import pymysql as mdb

import os

import sys
#
sys.path
sys.path.append('/home/pi/.local/lib/python2.7/site-packages')
#
import time
from datetime import datetime
import random 


        



if OURWEATHER_Present:
        import OURWEATHERFunctions
   #     import PubNubToSQL
        
if PubNub_Present:
        import PubNubToSQL
        import OURWEATHERFunctions
        import Msq1



from datetime import timedelta

from apscheduler.schedulers.background import BackgroundScheduler
import apscheduler.events

# constant defines

#How often in seconds to sample Data
#SampleTime = 0.01
SampleTime = 300.0  # point every 5 minutes, 288 in 24 hours
#How long in seconds to sample Data
#LengthSample = 120
LengthSample = 60
#When to generate graph (every how many minutes) 
GraphRefresh = 5.00
#GraphRefresh = 10.0
#How many samples to Graph
GraphSampleCount = 576  # 576 is graph for 48 hours


#mysql user
username = "datalogger"
#mysql Password
password = 'Data0233'
#mysql Table Name





# Main Program

print("")
print("SDL_Pi_Datalogger")
print("")
print(" Will work with OurWeather - Complete Weather Kit" )
print(" Will work with SwitchDoc Labs WxLink Wireless LInk " )
print("Program Started at:"+ time.strftime("%Y-%m-%d %H:%M:%S"))
print("")


filename = time.strftime("%Y-%m-%d%H:%M:%SRTCTest") + ".txt"
starttime = datetime.utcnow()



# setup apscheduler

def ap_my_listener(event):
        if event.exception:
              print(event.exception)
              print(event.traceback)

def tick():
    print('Tick! The time is: %s' % datetime.now()) 

def killLogger():
    scheduler.shutdown()
    print ("Scheduler Shutdown....")
    exit() 

def doAllGraphs():



    if OURWEATHER_Present:
        OURWEATHERFunctions.buildOURWEATHERGraphTemperature(username, password, GraphSampleCount)
        OURWEATHERFunctions.buildOURWEATHERGraphWind(username, password, GraphSampleCount)
        OURWEATHERFunctions.buildRainPerHourGraph(username, password, GraphSampleCount)
        OURWEATHERFunctions.buildOURWEATHERGraphSolarCurrent(username, password, GraphSampleCount)
        OURWEATHERFunctions.findOURWEATHERMaxTemperature(username, password)
        OURWEATHERFunctions.buildMyWeatherGraph(username, password, GraphSampleCount)

        
    if PubNub_Present:
        OURWEATHERFunctions.buildOURWEATHERGraphTemperature(username, password, GraphSampleCount)
        OURWEATHERFunctions.buildBarometricPressureGraph(username, password, GraphSampleCount)
        OURWEATHERFunctions.buildMyWeatherGraph(username, password, GraphSampleCount)
        OURWEATHERFunctions.buildOURWEATHERGraphWind(username, password, GraphSampleCount)
        OURWEATHERFunctions.buildOURWEATHERGraphTemperature(username, password, 288)
        OURWEATHERFunctions.buildOURWEATHERGraphTemperature(username, password, 576)
        OURWEATHERFunctions.buildOURWEATHERGraphTemperature(username, password, 2016)
        OURWEATHERFunctions.buildRainPerHourGraph(username, password, GraphSampleCount)




if __name__ == '__main__':

    scheduler = BackgroundScheduler()

    scheduler.add_listener(ap_my_listener, apscheduler.events.EVENT_JOB_ERROR)

    # make sure functions work before scheduling - may remove when debugged

    if OURWEATHER_Present:
        OURWEATHERFunctions.readOURWEATHERData(username, password)
        OURWEATHERFunctions.buildOURWEATHERGraphTemperature(username, password, GraphSampleCount)
        
    if PubNub_Present:
        #PubNubToSQL.doPubnub()
        Msq1.doMosquitto()
        #set up graphs
        OURWEATHERFunctions.buildOURWEATHERGraphTemperature(username, password, 288)
        OURWEATHERFunctions.buildOURWEATHERGraphTemperature(username, password, 576)
        OURWEATHERFunctions.buildOURWEATHERGraphTemperature(username, password, 2016)
        OURWEATHERFunctions.buildBarometricPressureGraph(username, password, GraphSampleCount)
        OURWEATHERFunctions.buildOURWEATHERGraphWind(username, password, GraphSampleCount)
        OURWEATHERFunctions.buildRainPerHourGraph(username, password, GraphSampleCount)






    if OURWEATHER_Present:
        scheduler.add_job(OURWEATHERFunctions.readOURWEATHERData, 'interval', seconds=SampleTime, args=[username, password])



    minuteCron = "*/"+str(int(GraphRefresh))
    scheduler.add_job(doAllGraphs, 'cron', minute=minuteCron )


    #scheduler.add_job(killLogger, 'interval', seconds=LengthSample)
    scheduler.add_job(tick, 'interval', seconds=120)
    scheduler.start()
    scheduler.print_jobs()

    print('Press Ctrl+{0} to exit'.format('Break' if os.name == 'nt' else 'C'))


    try:
        # This is here to simulate application activity (which keeps the main thread alive).
        while True:
            time.sleep(2)
    except (KeyboardInterrupt, SystemExit):
        # Not strictly necessary if daemonic mode is enabled but should be done if possible
        scheduler.shutdown()
        #
        print("Call to stopPubnub")
        PubNubToSQL.stopPubnub()
        sys.exit()









