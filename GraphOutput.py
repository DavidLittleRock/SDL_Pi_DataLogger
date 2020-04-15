import gc  # python garbage collector
import matplotlib
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

matplotlib.use('Agg')  # Force matplotlib to not use any Xwindows backend.
dataBaseName = 'DataLogger'
dataBaseTable = 'OURWEATHERTable'
username = 'datalogger'  # mySQL user
password = 'Data0233'  # mySQL password


def print_ts(txt='Variable ', msg=None):  # print with a time stamp
    dz = datetime.strftime(datetime.now(), '%H:%M, %A')
    print ("-" * 100)
    if msg is not None:
        print ("[{date}] {text} ==is =={message}".format(date=dz, text=txt, message=msg))
    else:
        print ("[{date}] {text} ".format(date=dz, text=txt))
    print ("-" * 100)


def build_temperature_and_humidity_graph(username, password, my_graph_sample_count):
    this_date = datetime.now()
    print_ts(txt='buildTemperatureAndHumidityGraph - The time is: {}'.format(datetime.now()))
    con1 = mdb.connect('localhost', username, password, dataBaseName)  # open mySQL database
    my_cursor = con1.cursor()

    days_to_print = [1, 2, 7]
    for days in days_to_print:
        query = '(SELECT timestamp, deviceid, Outdoor_Temperature, Outdoor_Humidity, id FROM ' + dataBaseTable + ' WHERE DATE(timestamp)>=Current_Date - ' + str(
            days) + ' LIMIT ' + str(my_graph_sample_count) + ') ORDER BY id ASC'
        try:
            my_cursor.execute(query)
            result = my_cursor.fetchall()
        except:
            e = sys.exc_info()[0]
            print ("Error: {}".format(e))
        time = []  # time
        temperature = []  # Outdoor temperature
        humidity = []  # Outdoor humidity
        for record in result:
            time.append(record[0])
            temperature.append((record[2] * 9 / 5) + 32)  # convert the temperature from C to F
            humidity.append(record[3])
        ave_temp = mean(temperature)
        max_temp = max(temperature)
        min_temp = min(temperature)
        fds = [dates.date2num(d) for d in
               time]  # time is a list of datetime.datetime objects and this converts to a float representation
        hfmt = dates.DateFormatter('%m/%d-%H')

        fig, ax = pyplot.subplots(figsize=(17.0, 8.0),
                                  facecolor='green')  # make figure(fig) with first subplot axes (ax)
        fig.suptitle('Temperature and Humidity, {} days'.format(days), fontsize=12)

        pyplot.xticks(rotation='45')
        pyplot.subplots_adjust(bottom=0.1, left=0.05)  # space from fig edge to axes edge
        pyplot.figtext(0.8, 0.9,
                       ('Average Temperature: {:6.2f} \n {} \n Max Temp: {:6.1f} Min Temp: {:6.1f}').format(ave_temp,
                                                                                                            datetime.strftime(
                                                                                                                this_date,
                                                                                                                '%c'),
                                                                                                            max_temp,
                                                                                                            min_temp),
                       fontsize=10, ha='left', va='bottom')
        pyplot.figtext(0.1, 0.9, 'Temperature now = {:6.1f}'.format(temperature[len(temperature) - 1]), fontsize=14,
                       ha='left', va='bottom')

        ax.grid(b='True', which='major', axis='both', linestyle='-', linewidth=2, color='black')
        ax.grid(b='True', which='major', axis='y', linewidth=1)
        ax.grid(b='True', which='minor', axis='x', linestyle='-.', color='black')
        ax.xaxis.set_major_formatter(hfmt)
        ax.xaxis.set_minor_locator(dates.HourLocator(interval=1))
        ax.xaxis.set_minor_locator(dates.HourLocator(byhour=(6, 12, 18)))
        ax.plot(fds, temperature, color='red', label="Outside Temp (F) ", linestyle="--",
                marker=".")  # x=fds(the matplotlib date number), y= u(temperature)
        ax.set_xlabel("Time")
        ax.set_ylabel("degrees F")
        ax.legend(loc='upper left')
        ax.axis([dates.date2num(datetime.now()) - days, dates.date2num(datetime.now()), 10, 110])

        #             ax = makeAx(ax, hfmt, fds, temperature, days)

        ax2 = ax.twinx()
        ax2.set_ylabel("% Humidity")
        ax2.plot(fds, humidity, color='blue', label="Outside Hum %", linestyle="--", marker=".")
        ax2.legend(loc='upper right')
        ax2.axis([dates.date2num(datetime.now()) - days, dates.date2num(datetime.now()), 10, 110])

        pyplot.savefig('/var/www/html/TemperatureAndHumidityGraph' + str(days) + '.png', facecolor=fig.get_facecolor())

    pyplot.show()
    mycursor.close()
    con1.close()
    fig.clf()
    pyplot.close()
    gc.collect()
    print_ts(txt='------TemperatureAndHumidityGraph finished now ------')


def build_wind_graph(username, password, my_graph_sample_count):
    dz = datetime.now()
    print_ts(txt='buildWindGraph - The time is: {}'.format(datetime.now()))
    con1 = mdb.connect('localhost', username, password, dataBaseName)
    my_cursor = con1.cursor()
    query = '(SELECT timestamp, deviceid, Current_Wind_Speed, Current_Wind_Gust, id FROM ' + dataBaseTable + ' WHERE DATE(timestamp) >= Current_Date - 7 LIMIT ' + str(
        my_graph_sample_count) + ') ORDER BY id ASC'
    try:
        my_cursor.execute(query)
        result = my_cursor.fetchall()
    except:
        e = sys.exc_info()[0]
        print ("Error: %s" % e)
    time = []  # time
    wind_speed = []  # Current Wind Speed
    gust = []  # Current Wind Gust
    for record in result:
        time.append(record[0])
        wind_speed.append(record[2] * 0.621)  # convert kph to mph
        gust.append(record[3] * 0.621)
    average_wind_speed = mean(wind_speed)
    wind_speed_sg = []
    gust_sg = []
    wind_speed_sg = signal.savgol_filter(wind_speed, 25, 5)  # apply the Savgo filter to smooth curve
    gust_sg = signal.savgol_filter(gust, 25, 5)
    fds = [dates.date2num(d) for d in time]  # converted
    hfmt = dates.DateFormatter('%m/%d-%H')
    fig, ax = pyplot.subplots(figsize=(17.0, 8.0), facecolor='red')
    fig.suptitle('Wind and Gust', fontsize=12)
    pyplot.xticks(rotation='45')
    pyplot.subplots_adjust(bottom=0.1, left=0.05)

    ax.grid(b='True', which='major', axis='both', linestyle='--')
    ax.xaxis.set_major_formatter(hfmt)
    ax.plot(fds, wind_speed_sg, color='red', label='Wind Speed (mph)', linestyle='solid', marker=".")
    ax.set_xlabel('Time')
    ax.set_ylabel('Wind (mph)')
    ax.legend(loc='upper left')
    ax.axis([dates.date2num(datetime.now()) - 2, dates.date2num(datetime.now()), 0, max(gustSG) + 1])

    ax2 = ax.twinx()
    ax2.plot(fds, gust_sg, color='blue', label='Wind Gust (mph)', linestyle='-.', marker='.')
    ax2.legend(loc='upper right')
    ax2.axis([dates.date2num(datetime.now()) - 2, dates.date2num(datetime.now()), 0, max(gustSG) + 1])

    pyplot.figtext(0.9, 0.9, ('Average Windspeed {AveWind:6.2f}\n{time}').format(AveWind=average_wind_speed,
                                                                                 time=datetime.strftime(dz, '%c')),
                   fontsize=12, ha='center')
    pyplot.show()
    pyplot.savefig("/var/www/html/WindAndGustGraph.png", facecolor=fig.get_facecolor())

    my_cursor.close()
    con1.close()
    fig.clf()
    pyplot.close()
    pylab.close()
    gc.collect()
    print ("------buildWindGraph finished now ------------")


def build_barometric_pressure_graph(username, password, my_graph_sample_count):
    dz = datetime.now()
    print('buildBarometricPressureGraph - The time is: %s' % datetime.strftime(dz, '%H:%M, %A'))
    con1 = mdb.connect('localhost', username, password, dataBaseName)
    my_cursor = con1.cursor()

    query = '(SELECT timestamp, deviceid, Barometric_Pressure, id FROM ' + dataBaseTable + ' WHERE DATE(timestamp) >= Current_Date - 7 LIMIT ' + str(
        my_graph_sample_count) + ') ORDER BY id ASC'
    try:
        my_cursor.execute(query)
        result = my_cursor.fetchall()
    except:
        e = sys.exc_info()[0]
        print ("Error: %s" % e)

    time = []  # time
    barometric_pressure = []  # Barometric Pressure

    for record in result:
        time.append(record[0])
        if record[2] is not None:
            barometric_pressure.append(round((record[2] / 3386.4), 2))
        elif record[2] is None:
            barometric_pressure.append(record[2])

    query_min_pres = '(SELECT min(Barometric_Pressure) FROM ' + dataBaseTable + ' )'
    query_max_pres = '(SELECT max(Barometric_Pressure) FROM ' + dataBaseTable + ' )'

    try:
        my_cursor.execute(query_min_pres)
        result_min_pres = my_cursor.fetchall()
    except:
        e = sys.exc_info()[0]
        print ("Error: %s" % e)
    try:
        my_cursor.execute(query_max_pres)
        result_max_pres = my_cursor.fetchall()
    except:
        e = sys.exc_info()[0]
        print ("Error: %s" % e)

    min_p = []
    for record in result_min_pres:
        min_p.append(round((record[0] / 3386.4), 2))
    max_p = []
    for record in result_max_pres:
        max_p.append(round((record[0] / 3386.4), 2))
    min_pres = min(min_p)
    if min_pres < 29:
        min_pres = 29.1
    max_pres = (max(max_p) + 0.01)
    fds = [dates.date2num(d) for d in time]

    hfmt = dates.DateFormatter('%m/%d-%H')

    fig, ax = pyplot.subplots(figsize=(17.0, 8.0), facecolor='blue')
    fig.suptitle('Barometric Pressure Graph', fontsize=12)
    pyplot.xticks(rotation='45')
    pyplot.subplots_adjust(bottom=0.1, left=0.05)
    pyplot.figtext(0.9, 0.9,
                   ("Barometric Pressure = {press:6.1f}\n{time}").format(press=barometric_pressure[len(time) - 1],
                                                                         time=datetime.strftime(dz, '%c')), fontsize=12,
                   ha='center')

    ax.grid(b='True', which='major', axis='both', linestyle='-', color='black')
    ax.xaxis.set_major_formatter(hfmt)
    ax.plot(fds, barometric_pressure, color='red', label="Barometric Pressure", linestyle="-", marker=".")
    ax.set_xlabel("Time")
    ax.set_ylabel("Pressure")
    ax.legend(loc='upper left', fontsize='x-small')
    ax.axis([dates.date2num(datetime.now()) - 7, dates.date2num(datetime.now()), min_pres, max_pres])
    ax.grid(True)

    pyplot.show()
    pyplot.savefig("/var/www/html/barometricPressureGraph.png", facecolor=fig.get_facecolor())

    my_cursor.close()
    con1.close()
    fig.clf()
    pyplot.close()
    pylab.close()
    gc.collect()
    print ("------baromrtricPressureGraph finished now-----------------")


#
#

def build_max_min_temperature_graph(username, password, my_graph_sample_count):
    dz = datetime.now()
    print('buildMaxMinTemperatureGraph - The time is: %s' % datetime.strftime(dz, '%H:%M, %A'))
    con1 = mdb.connect('localhost', username, password, dataBaseName)
    my_cursor = con1.cursor()
    query = '(SELECT Date, Max, Min FROM MinMaxTemp ) '  # ORDER BY Date  LIMIT 12

    try:
        my_cursor.execute(query)
        result = my_cursor.fetchall()
    except:
        e = sys.exc_info()[0]
        print ("Error: %s" % e)

    time = []  # Date
    max_temperature = []  # Max Temperature
    min_temperature = []  # Min Temperature

    for record in result:
        time.append(record[0])
        max_temperature.append((record[1] * 9 / 5) + 32)  # convert the temperature from C to F
        min_temperature.append((record[2] * 9 / 5) + 32)

    fig, ax = pyplot.subplots(figsize=(17.0, 8.0), facecolor='green')
    fig.suptitle("Daily Max and Min Temperature", fontsize=12)
    pyplot.xticks(rotation='45')
    fig.subplots_adjust(bottom=.1, left=0.1)

    ax.grid(b='True', which='major', axis='both', linestyle='--')
    ax.plot(time, max_temperature, color='r', label="Max Temp (F) ", linestyle="--", marker=".")
    ax.set_xlabel("Date")
    ax.set_ylabel("degrees F")
    ax.legend(loc='upper left')
    ax.axis([dates.date2num(datetime.now()) - 30, dates.date2num(datetime.now()), 10, 110])

    ax2 = ax.twinx()
    ax2.set_ylabel("degrees F")
    ax2.plot(time, min_temperature, color='b', label="Min Temp (F)", linestyle="-", marker=".")
    ax2.axis([dates.date2num(datetime.now()) - 30, dates.date2num(datetime.now()), 10, 110])
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


def yesterday_temperature():
    con1 = mdb.connect('localhost', username, password, dataBaseName)
    my_cursor = con1.cursor()
    query = '(SELECT Date, Max, Min FROM MinMaxTemp WHERE Date =  Current_Date - 1) '  # ORDER BY Date  LIMIT 12

    try:
        my_cursor.execute(query)
        result = my_cursor.fetchall()
    except:
        e = sys.exc_info()[0]
        print ("Error: %s" % e)

    print (result)
    print (result[0][1])


def make_ax(ax, hfmt, x, y, days):
    ax.grid(b='True', which='major', axis='both', linestyle='-', linewidth=2, color='black')
    ax.grid(b='True', which='major', axis='y', linewidth=1)

    ax.grid(b='True', which='minor', axis='x', linestyle='-.', color='black')
    ax.xaxis.set_major_formatter(hfmt)
    ax.xaxis.set_minor_locator(dates.HourLocator(interval=1))
    ax.xaxis.set_minor_locator(dates.HourLocator(byhour=(6, 12, 18)))

    ax.plot(x, y, color='red', label="Outside Temp (F) makeAx ", linestyle="--",
            marker=".")  # x=fds(the matplotlib date number), y= u(temperature)
    ax.set_xlabel("Time")
    ax.set_ylabel("degrees F")
    ax.legend(loc='upper left')
    ax.axis([max(x) - days, max(x), 10, 110])
    return ax


def build_rain_graph(username, password, my_graph_sample_count):
    this_date = datetime.now()
    print('buildRainGraph - The time is: %s' % datetime.now())
    con1 = mdb.connect('localhost', username, password,
                       dataBaseName)  # ('localhost', username, password, dataBaseName )
    my_cursor = con1.cursor()
    time = []  # time
    rain_period = []  # Outdoor temperature
    rain_total = []  # Outdoor humidity
    result = []
    days_to_print = [7, 6, 5, 4, 3, 2, 1, 0]
    for days in days_to_print:

        time_a = []
        rain_period_a = []
        rain_total_a = []

        query = '(SELECT id, timestamp, Rain_Change FROM RainPeriod WHERE DATE(timestamp)=Current_Date-' + str(
            days) + ' LIMIT ' + str(my_graph_sample_count) + ') ORDER BY id ASC'

        try:
            my_cursor.execute(query)
            result = my_cursor.fetchall()
        except:
            e = sys.exc_info()[0]
            print ("Error: %s" % e)

        for record in result:
            time_a.append(record[1])
            rain_period_a.append(record[2] / 22.5)
            rain_total_a.append(sum(rain_period_a))
        print ("count of time=", len(time))
        if len(timeA) != 0:
            time += time_a
            rain_period += rain_period_a
            rain_total += rain_total_a
    fds = [dates.date2num(d) for d in time]  # convert the datetime object from python to matplotlob time number
    hfmt = dates.DateFormatter('%m/%d-%H')

    fig, ax = pyplot.subplots(figsize=(17.0, 8.0), facecolor='green')  # make figure(fig) with first subplot axes (ax)
    fig.suptitle('Rain each day.', fontsize=12)
    pyplot.xticks(rotation='45')
    pyplot.subplots_adjust(bottom=0.1, left=0.05)  # space from fig edge to axes edge

    ax.grid(b='True', which='major', axis='both', linestyle='-', linewidth=2, color='black')
    ax.grid(b='True', which='major', axis='y', linewidth=1)
    ax.grid(b='True', which='minor', axis='x', linestyle='-.', color='black')
    ax.xaxis.set_major_formatter(hfmt)
    ax.xaxis.set_major_locator(dates.DayLocator(interval=1))
    ax.xaxis.set_minor_locator(dates.HourLocator(byhour=(6, 12, 18)))
    ax.plot(fds, rain_period, color='red', label="Rain this period ", linestyle="None",
            marker=".")  # x=fds(the matplotlib date number), y= u(temperature)
    ax.set_xlabel("Time")
    ax.set_ylabel("rain (inch)")
    ax.legend(loc='upper left')
    ax.axis([dates.date2num(datetime.now()) - 6, dates.date2num(datetime.now()), 0, max(rain_total) + 0.1])

    ax2 = ax.twinx()
    ax2.set_ylabel('Rain Total')
    ax2.plot(fds, rain_total, color='blue', label="Rain this day", marker='.', linestyle='None')
    ax2.legend(loc='upper right')
    ax2.axis([dates.date2num(datetime.now()) - 6, dates.date2num(datetime.now()), 0, max(rain_total) + 0.1])

    pyplot.savefig('/var/www/html/RainGraph.png', facecolor=fig.get_facecolor())
    pyplot.show()

    my_cursor.close()
    con1.close()
    fig.clf()
    pyplot.close()
    gc.collect()
    print ("------RainGraph finished now ------")
