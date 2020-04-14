import paho.mqtt.client as mqtt
# import time

broker_url = "192.168.1.201"
broker_port = 1883
payload = 0

def MQTTClient():
    def on_connect(self, userdata, flags, rc):
        print("connected with Result Code {}.".format(rc))

    def on_message(self, userdata, message):
        print("Message recieved: {}.".format(message.payload.decode()))
        print(type(message.payload.decode()))
        payload = message.payload.decode()
#        return payload
        
    def on_disconnect(self, userdata, rc):
        print("disconnedted")
        client.loop_stop()
        
    def on_subscribe(self, userdata, mid, granted_qos):
        print("subscribed")

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
    client.loop_start()

               

    #client.unsubscribe("OurWeather")
    #client.disconnect()
