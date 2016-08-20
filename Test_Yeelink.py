# -*- coding: utf-8 -*-
# **********************************************************
# * FileName：Test_Yeelink.py                                
# * Creater：Sunshine                                       
# * CreateTime：2015-11-26                                   
# * FileDesc：用于接收传感器上的数据，同时控制相关控制电路 
# ********************************************************************

import os
import re
import json  
import time  
import string
import serial
import requests
import RPi.GPIO as GPIO

# BOARD编号方式，基于插座引脚编号    
GPIO.setmode(GPIO.BOARD)    
# Define the 29 pin is output Mode  
GPIO.setup(29, GPIO.OUT) 
GPIO.setup(31, GPIO.OUT) 
GPIO.setup(33, GPIO.OUT) 
GPIO.setup(35, GPIO.OUT) 

# Define the serial msg
from time import sleep
ser = serial.Serial('/dev/ttyUSB0', 115200, timeout=0.5)

# define sensor's API URL and Apiheaders 
Apiurl_temp = 'http://api.yeelink.net/v1.0/device/342791/sensor/380250/datapoints'
Apiurl_humidity = 'http://api.yeelink.net/v1.0/device/342791/sensor/380251/datapoints'
Apiurl_soil_humi = 'http://api.yeelink.net/v1.0/device/342791/sensor/380252/datapoints'
Apiurl_Illumination = 'http://api.yeelink.net/v1.0/device/342791/sensor/380253/datapoints'

Apiurl_light = 'http://api.yeelink.net/v1.0/device/342791/sensor/380254/datapoints'
Apiurl_fan = 'http://api.yeelink.net/v1.0/device/342791/sensor/380491/datapoints'
Apiurl_curtain_on = 'http://api.yeelink.net/v1.0/device/342791/sensor/385392/datapoints'

Apiurl_Mode = 'http://api.yeelink.net/v1.0/device/342791/sensor/385510/datapoints'

apiheaders = {'U-ApiKey': 'c1cb356d594512603cee9d951d1d6830', 'content-type': 'application/json'} 

# The pin 29 is defined the Light state
# The pin 31 is defined the Fan state
# The pin 33 is defined the Curtain_On state
# The pin 35 is defined the Curtain_Off state

def Light_On():
     GPIO.output(29, GPIO.HIGH)  
def Light_Off():
    GPIO.output(29, GPIO.LOW)

def Fan_On():
     GPIO.output(31, GPIO.HIGH)
def Fan_Off():
    GPIO.output(31, GPIO.LOW)
    
def Curtain_On():
     GPIO.output(35, GPIO.LOW)
     GPIO.output(33, GPIO.HIGH)

def Curtain_Off():
     GPIO.output(33, GPIO.LOW)  
     GPIO.output(35, GPIO.HIGH)
       
# This function is To gain the net state that to contral the light.
def Gain_Light_State():
    r = requests.get(Apiurl_light, headers=apiheaders)
    Light_State = r.text
    if Light_State[-2] == '1':
        Light_On()
    elif Light_State[-2] == '0':
        Light_Off()
    else:
        pass        

def main():
    while True:
	#time.sleep(1.5)
        # Get the data from readline Serial
	data = ser.readline()
	s = re.findall(r'(\w*[0-9]+)\w*',data)
        if s:
	    s = int(s[1])
	    print data[0:10]
	    # Load the function Gain_Light_State that to contral the light
	    Gain_Light_State()
	    # Get the Manual automatic mode from the App to Auto_Mode
	    r = requests.get(Apiurl_Mode, headers=apiheaders)
	    Auto_Mode = r.text
	    if data[0:5] == 'DHT11':
                temp = s/100
                humidity = s-temp*100
                r = requests.get(Apiurl_fan, headers=apiheaders)
	        Fan = r.text
	        # The Auto_Mode[-2] == '1' express the auto mode is open or not.
	        # The Fan[-2] express r.text's last data the value of 'value'.
	        if(Auto_Mode[-2] == '1'):
	            if temp >= 30:
		        Fan_On()
        	    elif temp < 30:
	                Fan_Off()
	        elif(Auto_Mode[-2] == '0'):
	            if Fan[-2] == '1':
	                Fan_On()
	            elif Fan[-2] == '0':
	                Fan_Off()
                # send the Temp msg from raspberry to Yeelink
                payload = {'value': temp}
                r = requests.post(Apiurl_temp, headers=apiheaders, data=json.dumps(payload))
                # send the Humidity msg from raspberry to Yeelink
                payload = {'value': humidity}
                r = requests.post(Apiurl_humidity, headers=apiheaders, data=json.dumps(payload))
            elif data[0:5] == 'GY_30':
	        soil_humi = s*10
                # send the Humidity msg from raspberry to Yeelink
                payload = {'value': soil_humi}
                r = requests.post(Apiurl_soil_humi, headers=apiheaders, data=json.dumps(payload))
            elif data[0:5] == 'YL_41':
                Illumination = s
                # To express the mode is not Auto Mode
	        if(Auto_Mode[-2] == '0'):
	            print("This is not Auto Mode!")
	            r_on = requests.get(Apiurl_curtain_on, headers=apiheaders)
                    CurtainOn = r_on.text
	            # The Curtain_on[-2] express r.text's last data the value of 'value'
	            if CurtainOn[-2] == '1':
                        print("Curtain_On()")                        
                        Curtain_On()	                
	            else:
                        print("Curtain_Off()")
	                Curtain_Off()
	        # To express the mode is Auto Mode
	        elif(Auto_Mode[-2] == '1'):
	            print("This is Auto Mode!")
	            if(Illumination == 0):
	                Curtain_Off()
	                print("Curtain_Off()")
	            elif(Illumination == 1):
	                Curtain_On()
	                print("Curtain_On()")
	            else:
	                pass
                # send the Humidity msg from raspberry to Yeelink      (not(str(Illumination) == "10"))
                payload = {'value': (Illumination*10)}   
                r = requests.post(Apiurl_Illumination, headers=apiheaders, data=json.dumps(payload)) 
            else:
                # Empty Language            
                pass   
        else:
            pass      

if __name__ == '__main__':  
    main()  
