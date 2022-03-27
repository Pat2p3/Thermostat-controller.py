
#!/usr/bin/python

import Sensor as sensor
import time
import threading
import json 
import requests
import datetime
import logging

# global variables
threadLock = threading.Lock()
thread1 = None
poll_thread_started = False
temp_goal = 1.7 # degrees celcius

switch_address = "http://192.168.1.64/"
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
            self.polling = True # polls heater switch, otherwise heater turns off after timeout
            self.timeout = timeout

    def run(self):
        print("Starting polling eventLoop " + self.name)
        run_polling_loop = True

        while(run_polling_loop == True):

            self.lock.acquire() # LOCKED accessing polling
            run_polling_loop = self.polling
            self.lock.release() # UNLOCKED

            if run_polling_loop == True:
                try:
                    r = requests.get(switch_address + poll) #time intensive so accessed variable is copied to curr_polled_value
                    state = json.loads(r.text)
                    if state["state"] == "OFF":
                        turn_on_heater_http()                        
                    
                except Exception as e:      # can not reach Switch, http error, or json not formatted properly
                    out_text = "Exception: Stopping Polling, heater will shutdown after " + self.timeout + "second timeout. Exception: " + str(e) + " : " + str(datetime.datetime.now())
                    print(out_text)
                    logging.info(out_text)
                                        
                    run_polling_loop = False # update value

                    time.sleep(self.timeout)      
                        
            time.sleep(4) #sleep 4 seconds
            
    def turn_off_polling(self):

        self.lock.acquire() # LOCKED accessing polling

        self.polling = False
        global poll_thread_started
        poll_thread_started = False

        self.lock.release() # UNLOCKED        


def turn_off_heater_and_polling_locking():
    try:
        turn_off_heater_http()
        thread1.turn_off_polling() #locking and unlocked

    except Exception as e:      # can not reach Switch, http error, or json not formatted properly, lock problem
        out_text = "Exception: Heater shutting down, sleeping for " + str(thread1.timeout) + " second shutdown timeout. Exception =>: " + str(e)
        print(out_text)
        logging.info(out_text)
        
        time.sleep(thread1.timeout)

        if threadLock.locked():  # unlock
            threadLock.release()
"""
 Takes input boolean no_error, that is True on no error, False on error such that he sensor data could not be retrieved 
 due to sensor offline, or Exception
"""
def temp_change_callback(temperature, no_error): 
    
    out_text = "Callback: Temperature is :" + str(temperature) + " Celsius : " + str(datetime.datetime.now())
    print(out_text)
    logging.info(out_text)

    if no_error == False: # error, so shutdown
        turn_off_heater_and_polling_locking()
    elif no_error == True: # no error
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
    
    r = requests.get(switch_address + status) #time intensive so accessed variable is copied to curr_polled_value
    state = json.loads(r.text)
    state = state["state"]

    if state == "ERROR":
        state = "OFF"

    return state

if __name__=="__main__":

    out_text = "Target temperature : " + str(temp_goal) + " degrees Celcius : " + str(datetime.datetime.now())
    print(out_text)
    logging.info(out_text)

    thread1 = pollingThread(1, "Thread-1", threadLock) #init thread
    s = sensor.Sensor("192.168.1.136") # set sensor ip address

    temperature_sample_rate = 1

    while 1 == 1: # run forever unless crl+c in terminal
        s.getTemp(temp_change_callback)
        time.sleep(temperature_sample_rate)