# Thermostat-controller

Keeping a room just above freezing tyemperature is not possible with most space heaters. As they have a minmum setting that is too high.
Thermostat-controller.py polls the temperature_sensor.ino getting readings in celcius. When its too hot or cold the heater_controller.ino turns the space heater on or off. 
The heat turns on at temp_goal and off at temp_goal + 0.3 providing a 0.3 degree range. 

The source Thermostat-controller.py communicates with replicas temperature_sensor.ino and heater_controller.ino through http. 
All devices should be on the same local network. IP addresses of replicas are used in the Thermostat-controller.py 

## python variables
temp_goal set the temperature goal in Celcius, at this goal the heater turns on. At temp_goal + 0.3 it turns off.
switch_address is the address of the heater controller.

## Logging
Logging levels LOGGING.INFO, LOGGING.NOTSET - turns off logging.

## esp8266 variables
STASSID "Wifi SSID"
STAPSK  "Wifi password"
