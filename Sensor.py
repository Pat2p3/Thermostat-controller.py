import requests
import time

class Sensor:

    """
    Class connects to a http endpoint which returns the current temperature in celsius
    """
  
    # put class variables inside constructor
    def __init__(self, sensor_endpoint, logging = None):
        self.ip = sensor_endpoint
        self.most_freq = None
        self.count_dict = {}
        self.start_time = time.time()
        self.end_time = None
        self.max_count = 0
        self.last_sumbited_temp = None
        self.logging_Obj = logging
        print("Sensor initalized with ip: " + sensor_endpoint)

    # Takes messages and writes them to the log
    def logMesg(self, msg):
        if self.logging_Obj != None:
            self.logging_Obj.info(msg)

    
    # Takes a callback method and int interval(seconds) as inputs and gets Temperature data from REST API on sensor.
    # calls back on significant temperature change from previous temperature >= 0.125.
    # Temperature in callback is the most frequent(mode) of the temperatures sampled in the interval.
    def getTemp(self, callback, interval = 15):
        addr = "http://" + self.ip + "/temp" 
        
        try:
            r = requests.get(addr)
            temp = r.text

            if self.most_freq == None:
                self.most_freq = temp
                self.max_count = 1

            self.end_time = time.time() # move end time back

            count = self.count_dict.get(temp)
            if count == None: #not exists so set to 1
                self.count_dict.__setitem__(temp, 1) 
            else:
                self.count_dict[temp] = count + 1

                if count > self.max_count:
                    self.max_count = count
                    self.most_freq = temp

            if self.end_time - self.start_time > interval:   #15 secs is the interval roughly
                
                most_freq_temp = self.most_freq  #return value

                #reset values 
                self.most_freq = None
                self.max_count = 0
                self.start_time = time.time()
                self.count_dict = {}
                
                #only do callback initially and if temperature changed greater than the margin of error(0.125 degrees Celsius)
                
                if self.last_sumbited_temp == None:
                    self.last_sumbited_temp = most_freq_temp
                    callback(most_freq_temp, True)
                elif (abs(float(self.last_sumbited_temp) - float(most_freq_temp))) >= 0.125:
                    self.last_sumbited_temp = most_freq_temp
                    callback(most_freq_temp, True)
                
        except Exception as e:      # Temp Sensor not accessable, or Formatting issues
            error_text = "Exception -> sensor class -> getTemp : " + str(e)
            print(error_text)
            self.logMesg(error_text)

            callback(self.most_freq, False)
