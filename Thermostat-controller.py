
#!/usr/bin/python

import ListenerService as listener
import Sensor as sensor
import time
import threading
import json 
import requests
import datetime
import logging

from zeroconf import ServiceBrowser, ServiceListener, Zeroconf # python-zeroconf
import socket

# global variables
threadLock = threading.Lock()
thread1 = None
poll_thread_started = False
temp_goal = 1.7 # degrees celcius

switch_address = None # address for heater later assigned with mDNS 
toggle_on = "toggle_on"
toggle_off = "toggle_off"
status = "status"
poll = "poll"

logging.basicConfig(filename="heater_switch.log", level=logging.INFO) # NOTSET is for no logging

class pollingThread (threading.Thread):

    # Timeout in seconds
    def __init__(self, threadID, name, lock, timeout = 11):
            threading.Thread.__init__(self)
            self.threadID = threadID
            self.name = name
            self.lock = lock
            self.timeout = timeout
            self.run_polling_loop = False

    def run(self):
        print("Starting polling eventLoop " + self.name)
        self.run_polling_loop = True

        while(self.run_polling_loop == True):           
            
            try:
                r = requests.get(switch_address + poll) #time intensive
                state = json.loads(r.text)
                if state["state"] == "OFF":
                    turn_on_heater_http()                        
                    
            except Exception as e:      # can not reach Switch, http error, or json not formatted properly
                out_text = "Exception: Stopping Polling, heater will shutdown after " + self.timeout + "second timeout. Exception: " + str(e) + " : " + str(datetime.datetime.now())
                print(out_text)
                logging.info(out_text)
                                        
                self.run_polling_loop = False # update value
                self.turn_off_polling() # Locking unlocking shared boolean:poll_thread_started

                time.sleep(self.timeout)      

            time.sleep(self.timeout/3) # sleep
            
    def turn_off_polling(self):
        self.lock.acquire() # LOCKED accessing poll_thread_started
        global poll_thread_started
        poll_thread_started = False
        self.run_polling_loop = False

        self.lock.release() # UNLOCKED        


def turn_off_heater_and_polling_locking():
    try:
        thread1.turn_off_polling() #locking and unlocked
        turn_off_heater_http()

    except Exception as e:      # can not reach Switch, http error, or json not formatted properly, lock problem
        out_text = "Exception: Heater shutting down, sleeping for " + str(thread1.timeout) + " second shutdown timeout. Exception =>: " + str(e)
        print(out_text)
        logging.info(out_text)
        
        time.sleep(thread1.timeout)

"""
 Takes input boolean no_error, that is True on no error, False on error such that he sensor data could not be retrieved 
 due to sensor offline, or Exception
"""
def temp_change_callback(temperature, no_error): 
    
    if no_error == False: # error, so shutdown
        turn_off_heater_and_polling_locking()
    elif no_error == True: # no error
        out_text = "Callback: Temperature is :" + str(temperature) + " Celsius : " + str(datetime.datetime.now())
        print(out_text)
        logging.info(out_text)

        if float(temperature) >= temp_goal + 0.3: #turn off, at 2.3 when goal is 2.0
            turn_off_heater_and_polling_locking()
        elif float(temperature) <= temp_goal:   # turn on, at 2.0 when goal is 2.0
            power_on_heater_and_run_polling_locking()

def turn_on_heater_http():

    state = get_heater_state()

    if state == "OFF":
        r = requests.get(switch_address + toggle_on)
        state = json.loads(r.text)
        state = state["state"]

        if state == "OFF" or state == "ERROR":
            raise Exception("EXCEPTION: failed turn on : ") + str(datetime.datetime.now()) 
        else:
            out_text = "turned on heater : " + str(datetime.datetime.now()) 
            print(out_text)
            logging.info(out_text)

def turn_off_heater_http():

    state = get_heater_state()

    if state == "ON":
        r = requests.get(switch_address + toggle_off)
        state = json.loads(r.text)
        state = state["state"]

        if state == "ON" or state == "ERROR":
            raise Exception("EXCEPTION: failed http toggle off : ") + str(datetime.datetime.now()) 
        else:
            out_text = "turned off heater :" + str(datetime.datetime.now())
            print(out_text)
            logging.info(out_text)
                
def power_on_heater_and_run_polling_locking():
    global poll_thread_started
    global thread1
    global threadLock

    thread1.lock.acquire() # LOCK 

    if poll_thread_started == False:
        try:

            thread1 = pollingThread(1, "Thread-1", threadLock)
            thread1.start()

            poll_thread_started = True
        except Exception as e:
            out_text = "Error: unable to start polling thread, or failed to turn on heater" + str(e)
            print(out_text)
            logging.info(out_text)

            poll_thread_started = False
            

    thread1.lock.release() # UNLOCK
      
def get_heater_state():
    
    r = requests.get(switch_address + status) #time intensive
    state = json.loads(r.text)
    state = state["state"]

    if state == "ERROR":
        state = "OFF"

    return state


if __name__=="__main__":
    
    try:
        
        heater_service = ['_heater_cont._tcp.local.', 'esp8266_hh._heater_cont._tcp.local.'] # type, name 
        h_ip, h_port = listener.mDNS.serviceStatus(heater_service)

        sensor_service = ['_sensor_._tcp.local.', 'esp8266_h._sensor_._tcp.local.']
        s_ip, s_port = listener.mDNS.serviceStatus(sensor_service)

        if h_ip != None:
            switch_address = "http://" + str(h_ip) + "/"
        else:
            out_text = "Not found heater"
            print(out_text)
            logging.info(out_text)

        # if sensor is alive but heater is not, start anyways to log temperature
        # TODO: save temperatures to db

        if s_ip != None:       

            out_text = "Target temperature : " + str(temp_goal) + " degrees Celcius : " + str(datetime.datetime.now())
            print(out_text)
            logging.info(out_text)

            thread1 = pollingThread(1, "Thread-1", threadLock) #init thread
            s = sensor.Sensor(s_ip, logging) # set sensor ip address

            temperature_sample_rate = 1

            while 1 == 1: # run forever unless crl+c in terminal
                s.getTemp(temp_change_callback)
                time.sleep(temperature_sample_rate)

        else:
            out_text = "Not found temperature sensor"
            print(out_text)
            logging.info(out_text)


    except Exception as e:
            out_text = "Failed mDNS, Exception: " + str(e)
            print(out_text)
            logging.info(out_text)
            