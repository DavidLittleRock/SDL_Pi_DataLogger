from datetime import datetime
import MySQLdb as mdb
import paho.mqtt.client as mqtt
# import json
# import OURWEATHERFunctions
import GraphOutput
import SendEmail
# import MQTTClient
import time

broker_url = '192.168.1.201'
broker_port = 1883
dataBaseName = 'DataLogger'
dataBaseTable = 'OURWEATHERTable'
username = 'datalogger'  # mysql user
password = 'Data0233'  # mysql
hostName = 'localhost'


def print_ts(txt='Variable ', msg=None):  # print with a time stamp
    dz = datetime.strftime(datetime.now(), '%H:%M, %A')
    print ("-" * 100)
    if msg is not None:
        print ("[{}] {} ==is =={}".format(dz, txt, msg))
    else:
        print ("[{}] {} ".format(dz, txt))
    print ("-" * 100)


def on_connect(self, userdata, flags, rc):
    print_ts(txt='connected with Result Code {}.'.format(rc))


def on_message(self, userdata, message):
    print_ts(txt='Message recieved: ', msg=message.payload.decode())
    payload = message.payload.decode()
    w_data_2 = parse_data(payload)
    print_ts(txt='Message parsed')

    write_to_db(w_data_2)
    print_ts(txt='sent to DB')


def on_disconnect(self, userdata, rc):
    print_ts(txt='disconnected with rc ', msg=rc)


#  client.loop_stop()

def on_subscribe(self, userdata, mid, granted_qos):
    print_ts(txt='subscribed')


def mqtt_client():
    client = mqtt.Client(client_id="myWeatherId", clean_session=True, userdata=None, transport="tcp")
    client.on_connect = on_connect
    client.on_message = on_message
    client.on_disconnect = on_disconnect
    client.on_subscribe = on_subscribe
    client.connect(broker_url, broker_port)
    try:
        client.subscribe('OurWeather')
    except:
        print("subscribe error")
    client.loop_start()  # will automatically call on_message


def parse_data(payload):
    payload = payload.replace('{', '')
    payload = payload.replace('}', '')
    payload = payload.replace('"', '')
    index = (payload.index("ing") + 5)
    string_1 = payload[index:]
    string_2 = string_1.split(",")
    return string_2


def write_to_db(w_data_2):
    # open database
    con = mdb.connect('localhost', username, password, dataBaseName)
    cur = con.cursor()

    device_id = 5
    query = 'INSERT INTO ' + dataBaseTable + (
                '(timestamp, device_id, Outdoor_Temperature , Outdoor_Humidity , Barometric_Pressure , Current_Wind_Speed , Current_Wind_Gust , Current_Wind_Direction , Wind_Speed_Maximum , Wind_Gust_Maximum , OurWeather_DateTime , Lightning_Time , Lightning_Distance , Lightning_Count , Rain_Total , Rain_Now) VALUES(CURRENT_TIMESTAMP,  %i, %.3f, %.3f, %.3f, %.3f, %.3f, %.3f, %.3f, %.3f, "%s", "%s", %i, %i, %.2f, %.3f)' % (
        int(device_id), float(w_data_2[0]), float(w_data_2[1]), float(w_data_2[2]), float(w_data_2[3]), float(w_data_2[4]),
        float(w_data_2[5]), float(w_data_2[7]), float(w_data_2[8]), w_data_2[9], w_data_2[10], int(w_data_2[11]), int(w_data_2[12]),
        float(w_data_2[6]), float(w_data_2[13])))

    print_ts(txt='query ', msg=query)

    cur.execute(query)
    con.commit()


def make_graph():
    GraphOutput.build_temperature_and_humidity_graph(username, password, 5100)
    GraphOutput.build_wind_graph(username, password, 5100)
    GraphOutput.build_barometric_pressure_graph(username, password, 15000)
    GraphOutput.build_max_min_temperature_graph(username, password, 40)
    GraphOutput.build_rain_graph(username, password, 5100)


def main():
    print_ts(txt='start main')
    mqtt_client()
    print_ts(txt='main')

    #    GraphOutput.yesterdayTemperature()
    while True:
        try:
            time.sleep(60)
            make_graph()
        except Exception, e:
            print(e)
            print("done")


if __name__ == '__main__':
    main()
