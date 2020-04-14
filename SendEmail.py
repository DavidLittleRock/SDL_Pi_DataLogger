
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime
import MySQLdb as mdb
import gc
import sys


dataBaseName = "DataLogger"
dataBaseTable = 'OURWEATHERTable'
#mysql user
username = "datalogger"
#mysql Password
password = 'Data0233'

def sendEmail(message, rain):
    host = "smtp.gmail.com"
    port =  587
    username = "DavidWeatherStation@gmail.com"
    password = "Weather123"
    toname = "David.king.lr@gmail.com"
#    message ="a message 2"
    print(message)
    email_conn =  smtplib.SMTP(host, port)
    email_conn.ehlo()
    email_conn.starttls()

    try:
        email_conn.login(username, password)
    except smtplib.SMTPAuthenticationError:
        print ("could not log in")
    
    maxTemp = ((message[0]*9/5)+32)
    minTemp = ((message[1]*9/5)+32)
    message2 = "This is a automatic message form David's Weather Station. The high temperature yesterday was {:.1f} and the low was {:.1f}.".format(maxTemp, minTemp)
#    email_conn.sendmail(username, toname, message2)


    the_msg = MIMEMultipart("alternative")

    the_msg["Subject"] = "Hello, from David's Weather Station"
    the_msg["From"] = username
    the_msg["To"] = toname
    body = "str(maxTemp)"
    plain_txt = "Testing the message"
    html_txt = """\
    <html>
     <head></head>
      <body>
       This is a automatic message from David's Weather Station. <br>
       The high temperature yesterday was <b>{:.1f}F</b> and the low was <b>{:.1f}F</b>.<br>
       Rain was {:.1f} inches.<br>
       Thank You.
      </body>
    </html>
    """
    html_txt_2 = html_txt.format(maxTemp, minTemp, rain)
    part_1 = MIMEText(plain_txt, "plain")
    part_2 = MIMEText(html_txt_2, "html")

    the_msg.attach(part_1)
    the_msg.attach(part_2)
    email_conn.sendmail(username, toname, the_msg.as_string())

    print(the_msg.as_string())

def getTemperature():
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
    
    mycursor.close()         
    con1.close()

    gc.collect()
    
    return (result[0][1], result[0][2])

def getRain():
     # open database
    con1 = mdb.connect('localhost', username, password, dataBaseName )
    # now we have to get the data, stuff it in the graph 
    mycursor = con1.cursor()
    query = '(SELECT OurWeather_DateTime, SUM(Rain_Change)/22.5 FROM Rain_Period WHERE DATE(OurWeather_DateTime) =  Current_Date - 1) ' # ORDER BY Date  LIMIT 12

    print ("query=", query)
    try:
        mycursor.execute(query)
        result = mycursor.fetchall()
    except:
        e=sys.exc_info()[0]
        print ("Error: %s" % e)

    print (result)
    print (result[0][1])
    
    mycursor.close()         
    con1.close()

    gc.collect()
    rain = result[0][1]
    print (rain)
    if rain == None:
        rain = 0
    return rain




def main():
    rain = getRain()

    message = getTemperature()
    print(message)
    sendEmail(message, rain)

if __name__ == '__main__':
    main()
