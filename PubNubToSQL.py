#PubNub
import json

#import pubnub pubnub.com/docs/python/pubnub-python-sdk
from pubnub.pubnub import PubNub
from pubnub.enums import PNStatusCategory, PNOperationType
from pubnub.callbacks import SubscribeCallback
from pubnub.pnconfiguration import PNConfiguration
pnconfig = PNConfiguration()
pnconfig.subscribe_key = 'sub-c-911576ee-7967-11e9-89f1-56e8a30b5f0e'
pnconfig.publish_key = 'pub-c-db0a76ee-2837-4015-8c80-fd01dd0e7f3a'
pnconfig.uuid = 'dave'
pubnub = PubNub(pnconfig)

#
from datetime import datetime
import MySQLdb as mdb
#
DebugOn = False

class MySubscribeCallback(SubscribeCallback):
    def status(self, pubnub, status):

        # The status object returned is always related to subscribe but could contain
        # information about subscribe, heartbeat, or errors
        # use the operationType to switch on different options
        if status.operation == PNOperationType.PNSubscribeOperation \
                or status.operation == PNOperationType.PNUnsubscribeOperation:
            if status.category == PNStatusCategory.PNConnectedCategory:
                pass
                # This is expected for a subscribe, this means there is no error or issue whatsoever
            elif status.category == PNStatusCategory.PNReconnectedCategory:
                pass
                # This usually occurs if subscribe temporarily fails but reconnects. This means
                # there was an error but there is no longer any issue
            elif status.category == PNStatusCategory.PNDisconnectedCategory:
                pass
                # This is the expected category for an unsubscribe. This means there
                # was no error in unsubscribing from everything
            elif status.category == PNStatusCategory.PNUnexpectedDisconnectCategory:
                pass
                # This is usually an issue with the internet connection, this is an error, handle
                # appropriately retry will be called automatically
            elif status.category == PNStatusCategory.PNAccessDeniedCategory:
                pass
                # This means that PAM does not allow this client to subscribe to this
                # channel and channel group configuration. This is another explicit error
            else:
                pass
                # This is usually an issue with the internet connection, this is an error, handle appropriately
                # retry will be called automatically
        elif status.operation == PNOperationType.PNSubscribeOperation:
            # Heartbeat operations can in fact have errors, so it is important to check first for an error.
            # For more information on how to configure heartbeat notifications through the status
            # PNObjectEventListener callback, consult http://www.pubnub.com/docs/python/api-reference-configuration#configuration
            if status.is_error():
                pass
                # There was an error with the heartbeat operation, handle here
            else:
                pass
                # Heartbeat operation was successful
        else:
            pass
            # Encountered unknown status type

    def presence(self, pubnub, presence):
        # pass  # handle incoming presence data
        print("call to presence")

    def message(self, pubnub, message):
        print ("call to message")
        #pass  # handle incoming messages
        DebugOn = True
        if DebugOn:
           print("Message from PubNub= ", message.message)
           print type (message.message)
           # pre split weather data
        data=message.message
        print ("Data PubNub= ", data)
        print type (data)
        preSplitData = data['FullDataString'] # change to DataLoggerDataSting froom FullDataString
        if DebugOn:
            print("preSplitData from PubNub= ", preSplitData)
            print type (preSplitData)
            
        WData = preSplitData.split(",")
        if DebugOn:
            print ("WData array from PubNub= ", WData)
        
        con = mdb.connect('localhost', 'datalogger', 'Data0233', 'DataLogger')
        cur = con.cursor()

    #
    # Now put the data in MySQL
    # 
        # Put record in MySQL

        print ("writing SQLdata ");

        OURWEATHERtableName = 'OURWEATHERTable'

        # write record
        deviceid = 2
    ##    in query below I substract 6 hours fron UTC_TIMESTAMP to convert to central time
        query = 'INSERT INTO '+OURWEATHERtableName+('(timestamp, deviceid, Outdoor_Temperature , Outdoor_Humidity , Barometric_Pressure , Current_Wind_Speed , Current_Wind_Gust , Current_Wind_Direction , Wind_Speed_Maximum , Wind_Gust_Maximum , Display_English_Metric , OurWeather_DateTime , Lightning_Time , Lightning_Distance , Lightning_Count, Rain_Total, Rain_Now) VALUES(UTC_TIMESTAMP() - INTERVAL 6 HOUR,  %i, %.3f, %.3f, %.3f, %.3f, %.3f, %.3f, %.3f, %.3f, %i, "%s" , "%s", %i, %i, %.2f, %2f)' % ( int(deviceid), float(WData[0]), float(WData[1]), float(WData[3]), float(WData[5]), float(WData[6]), float(WData[7]), float(WData[10]), float(WData[12]), int(WData[15]), WData[16], WData[36], int(WData[37]), int(WData[40]), float(WData[8]), float(WData[59]))) 
# need way to do id so  not hard coded as 1 deviceid
        print("query=%s" % query)

        cur.execute(query)  
        con.commit()

    def signal(self, pubnub, signal):
        #pass # handle incoming signals
        print("call to signal")
def doPubnub():
    print("************ doPubNub ****************")
    pubnub.add_listener(MySubscribeCallback())
    pubnub.subscribe().channels('OWIOT1').execute()
    
def stopPubnub():
    pubnub.unsubscribe().channels('OWIOT1').execute()

