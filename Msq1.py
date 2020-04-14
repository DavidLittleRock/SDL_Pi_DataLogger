import paho.mqtt.subscribe as subscribe
import json
import ast
#
from datetime import datetime
import MySQLdb as mdb

# client = mqtt.Client()
#client.connect("localhost",1883)
# msg = subscribe.simple("OurWeather",hostname="localhost")
#client.publish(topic="OurWeather", payload="test",qos=1,retain=False)
# print("%s %s" %(msg.topic, msg.payload))
def on_message(client, userdata, message):
    print ("Topic= %s Payload= %s" %(message.topic, message.payload))
        
    data=message.payload
    print ("1 payload = ",data)
    print type(data)
    
    datab = data.replace("\"","")
    print("2 remove \" = ",datab)
    print type (datab)

    datad = json.dumps(datab)
    print ("3 after json dumps string to json = ",datad)
    print type (datad)
    
    datal = json.loads(datad)
    print ("4 after json loads json to string = ",datal)
    print type (datal)
     
    WData = datal.split("FullDataString:")
    print ("5 WData after split on FullDataString: = ", WData)
    print type (WData)
    
    print ("6 Wdata[1] = ", WData[1])
    print type (WData[1])
    
    WData2 = WData[1]
    print ("7 WData2", WData2)
    print type (WData2)
    
    WData2 = WData2.split(",")
    print ("8 WData2", WData2)
    print type (WData2)
    [str(x) for x in WData2]
    print ("9 WData2" , WData2)
    print type (WData2)
    
    print (WData2[17])
    con = mdb.connect('localhost', 'datalogger', 'Data0233', 'DataLogger')
    
    
    
    cur = con.cursor()

    #
    # Now put the data in MySQL
    # 
        # Put record in MySQL

    print ("writing SQLdata ");

    OURWEATHERtableName = 'OURWEATHERTable'

        # write record
    deviceid = 3
    ##    in query below I substract 6 hours fron UTC_TIMESTAMP to convert to central time
    query = 'INSERT INTO '+OURWEATHERtableName+('(timestamp, deviceid, Outdoor_Temperature , Outdoor_Humidity , Barometric_Pressure , Current_Wind_Speed , Current_Wind_Gust , Current_Wind_Direction , Wind_Speed_Maximum , Wind_Gust_Maximum , Display_English_Metric , OurWeather_DateTime , Lightning_Time , Lightning_Distance , Lightning_Count) VALUES(UTC_TIMESTAMP() - INTERVAL 6 HOUR,  %i, %.3f, %.3f, %.3f, %.3f, %.3f, %.3f, %.3f, %.3f, %i, "%s" , "%s", %i, %i)' % ( int(deviceid), float(WData2[0]), float(WData2[1]), float(WData2[3]), float(WData2[5]), float(WData2[6]), float(WData2[7]), float(WData2[10]), float(WData2[12]), int(WData2[15]), WData2[16], WData2[36], int(WData2[37]), int(WData2[40]), float(WData2[8]))) 
# need way to do id so  not hard coded as 1 deviceid
    print("query=%s" % query)

    cur.execute(query)  
    on.commit()
    
    
def doMosquitto():
    subscribe.callback(on_message, "OurWeather",hostname="localhost")
