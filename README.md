# Thermostat-controller

Keeping a room just above freezing tyemperature is not possible with most space heaters. As they have a minmum setting that is too high.
Thermostat-controller.py polls the temperature_sensor.ino getting readings in celcius. When its too hot or cold the heater_controller.ino turns the space heater on or off.

The source Thermostat-controller.py communicates with replicas temperature_sensor.ino and heater_controller.ino through http. 
All devices should be on the same local network. IP addresses of replicas are used in the Thermostat-controller.py. The ds18b20 temperature sensor is used in the replica. 

## python variables
temp_goal set the temperature goal in Celcius, at this goal the heater turns on. At (temp_goal + 0.3) it turns off.

## Logging
Logging levels LOGGING.INFO, LOGGING.NOTSET - turns off logging.

## esp8266 variables
STASSID "Wifi SSID" <br />
STAPSK  "Wifi password" <br />

## Connectivity
This project uses Multicast DNS to automatically discover the ip addresses of replicas.
