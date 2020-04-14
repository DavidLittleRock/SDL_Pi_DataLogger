from datetime import datetime
import MySQLdb as mdb
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


def print_ts(txt = 'Variable ', msg = None):  # print with a time stamp
    dz = datetime.strftime(datetime.now(), '%H:%M, %A')
    print ("-"*100)
    if msg is not None:
        print ("[{}] {} ==is =={}".format(dz, txt, msg))
    else:
        print ("[{}] {} ".format(dz, txt))
    print ("-"*100)


def on_connect(self, userdata, flags, rc):
    print_ts (txt = 'connected with Result Code {}.'.format(rc))


def on_message(self, userdata, message):
    print_ts (txt = 'Message recieved: ', msg = message.payload.decode())
    payload = message.payload.decode()
    WData2 = parseData(payload)
    print_ts (txt = 'Message parsed')
    
    writeToDb(WData2)
    print_ts (txt = 'sent to DB')
    
    
def on_disconnect(self, userdata, rc):
    print_ts (txt = 'disconnedted with rc ', msg = rc)
  #  client.loop_stop()
    
def on_subscribe(self, userdata, mid, granted_qos):
    print_ts (txt = 'subscribed')


def MQTTClient():
    client = mqtt.Client(client_id="myWeatherId", clean_session=True, userdata=None, transport="tcp")
    client.on_connect = on_connect
    client.on_message = on_message
    client.on_disconnect = on_disconnect
    client.on_subscribe = on_subscribe
    client.connect(broker_url, broker_port)
    try:
        client.subscribe("OurWeather")
    except:
        print("subscribe error")
    client.loop_start()  # will automatically call on_message


def parseData(payload):
    payload = payload.replace('{','')
    payload = payload.replace('}','')
    payload = payload.replace('"','')
    index = (payload.index("ing")+ 5)
    string1 = payload[index:]
    string2 = string1.split(",")
    return string2

def writeToDb(WData2):
   # open database
    con = mdb.connect('localhost', username, password, dataBaseName )
    cur = con.cursor()

    deviceid = 5
    query = 'INSERT INTO '+dataBaseTable+('(timestamp, deviceid, Outdoor_Temperature , Outdoor_Humidity , Barometric_Pressure , Current_Wind_Speed , Current_Wind_Gust , Current_Wind_Direction , Wind_Speed_Maximum , Wind_Gust_Maximum , OurWeather_DateTime , Lightning_Time , Lightning_Distance , Lightning_Count , Rain_Total , Rain_Now) VALUES(CURRENT_TIMESTAMP,  %i, %.3f, %.3f, %.3f, %.3f, %.3f, %.3f, %.3f, %.3f, "%s", "%s", %i, %i, %.2f, %.3f)' % ( int(deviceid), float(WData2[0]), float(WData2[1]), float(WData2[2]), float(WData2[3]), float(WData2[4]), float(WData2[5]), float(WData2[7]), float(WData2[8]), WData2[9], WData2[10], int(WData2[11]), int(WData2[12]), float(WData2[6]), float(WData2[13]))) 

    print_ts (txt = 'query ', msg = query)

    cur.execute(query)  
    con.commit()
    
    
def makeGraph():
    GraphOutput.buildTemperatureAndHumidityGraph(username, password, 5100)
    GraphOutput.buildWindGraph(username, password, 5100)
    GraphOutput.buildBarometricPressureGraph(username, password, 15000)
    GraphOutput.buildMaxMinTemperatureGraph(username, password, 30)
    GraphOutput.buildRainGraph(username, password, 5100)


def main():
    print_ts (txt = 'start main')
    MQTTClient()
    print_ts (txt = 'main')
 
#    GraphOutput.yesterdayTemperature()
    while True:
        try:
            time.sleep(60)
            makeGraph()
        except Exception, e:
            print(e)
            print("done")


if __name__ == '__main__':
    main()