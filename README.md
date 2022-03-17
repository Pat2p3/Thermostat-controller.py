# temp_sensor
A Thermostat the allows low temperature settings. An esp8266 microcontroller takes temperature readings in celcius and another powers the heater on or off.
The python controller and all the esp8266 controllers have to be on the same network.

## python variables
temp_goal set the temperature goal in Celcius, at this goal the heater turns on. At temp_goal + 0.3 it turns off.
switch_address is the address of the heater controller

## esp8266 variables
STASSID "Wifi SSID"
STAPSK  "Wifi password"

## How it works

