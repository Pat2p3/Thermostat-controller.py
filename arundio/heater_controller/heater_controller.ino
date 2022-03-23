#include <ESP8266WiFi.h>
#include <WiFiClient.h>
#include <ESP8266WebServer.h>
#include <ESP8266mDNS.h>
#include <stdbool.h> 
#include "TimeLib.h" //https://github.com/PaulStoffregen/Time time library used

/*
 * The space heater has a power button and its own interal circuity. 
 * This project stimulates the press of the power button to turn the heater on/off
*/


#ifndef STASSID
#define STASSID "WIFI SSID"
#define STAPSK  "Password"
#endif

#define TIME_HEADER  "T"   // Header tag for serial time sync message
#define TIME_REQUEST  7    // ASCII bell character requests a time sync message 

const char* ssid = STASSID;
const char* password = STAPSK;

bool IS_ON = false;
bool polled = false;


const int relayPin = D0;
void ron(){  digitalWrite(relayPin, LOW); Serial.println("on");}
void roff(){  digitalWrite(relayPin, HIGH); Serial.println("off");}

const unsigned long DEFAULT_TIME = 1357041600; // Arbitrary time starting point. Only used for measuring time passed not the present time.
time_t start = DEFAULT_TIME;
time_t end = DEFAULT_TIME;

ESP8266WebServer server(80);

void setup(void) {
  pinMode(relayPin, OUTPUT); 
  roff();

//code from timer
  Serial.begin(115200);
  while (!Serial) ; // Needed for Leonardo only
  pinMode(13, OUTPUT);

   // Jan 1 2013 arbitrary time, so can can difference in start, end times
  setTime(DEFAULT_TIME);
  end = now();
  
  Serial.println("Waiting for sync message");
//timer
  
  //Serial.begin(115200);
  WiFi.mode(WIFI_STA);
  WiFi.begin(ssid, password);
  Serial.println("");

  // Wait for connection
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("");
  Serial.print("Connected to ");
  Serial.println(ssid);
  Serial.print("IP address: ");
  Serial.println(WiFi.localIP());

  if (MDNS.begin("esp8266")) {
    Serial.println("MDNS responder started");
  }

  server.on("/", handleRoot);
  server.on("/toggle_on", turn_on_toggle);
  server.on("/toggle_off", turn_off_toggle);
  
  server.on("/poll", poll);
  server.on("/status", status);
  server.onNotFound(handleNotFound);
  server.begin();
  Serial.println("HTTP server started");
}

void handleRoot() {
  server.send(200, "text/plain", "hello from esp8266!\r\n");
}

void handleNotFound() {
  String message = "File Not Found\n\n";
  message += "URI: ";
  message += server.uri();
  message += "\nMethod: ";
  message += (server.method() == HTTP_GET) ? "GET" : "POST";
  message += "\nArguments: ";
  message += server.args();
  message += "\n";
  for (uint8_t i = 0; i < server.args(); i++) {
    message += " " + server.argName(i) + ": " + server.arg(i) + "\n";
  }
  server.send(404, "text/plain", message);
}

void poll(){
  polled = true; //return state [ON|OFF]
  send_state();
  Serial.println("Polled:");
  digitalClockDisplay();
}

void status(){
  Serial.println("Sending Status update");
  send_state();
}

void send_state(){
  if(IS_ON == true){
    server.send(200, "text/plain", " { \"state\": \"ON\" }\r\n");
  }
  else if(IS_ON == false){
    server.send(200, "text/plain", " { \"state\": \"OFF\" }\r\n");
  }
  else{
    server.send(200, "text/plain", " { \"state\": \"ERROR\" }\r\n");
  }
}

// add connection breaking check if sensor dies then will turn off this relay. Use polling, or sockets
void toggle(){
  polled = true;
  toggle_logic();
  send_state();
}

void toggle_logic(){
  ron();
  delay(1000);
  roff();
  bool state = IS_ON;
  IS_ON = !state;
  
  if(IS_ON){
    Serial.println("toggled ON");
    digitalClockDisplay();
  }
  else{
    Serial.println("toggled OFF");
    digitalClockDisplay();
  }
}

void turn_off_toggle(){
  if(IS_ON){
    toggle_logic();
    send_state();
  }
  else{
    send_state();
  }
}

void turn_on_toggle(){
  if(IS_ON == false){
    toggle_logic();
    send_state();
  }  
  else{
    send_state();
  }
}

void printDigits(int digits){
  // utility function for digital clock display: prints preceding colon and leading 0
  Serial.print(":");
  if(digits < 10)
    Serial.print('0');
  Serial.print(digits);
}

void digitalClockDisplay(){
  // digital clock display of the time
  Serial.print(hour());
  printDigits(minute());
  printDigits(second());
  Serial.print(" ");
  Serial.print(day());
  Serial.print(" ");
  Serial.print(month());
  Serial.print(" ");
  Serial.print(year()); 
  Serial.println(); 
}

void loop(void) {
  server.handleClient();
  MDNS.update();

  end = now();

  time_t diff = end - start;

  if(diff >= 10){
    time_t rightnow = now();
    start = rightnow;
    end = rightnow;
    diff = 0;
    if(IS_ON == true && polled == false){
      toggle_logic();
    }
    polled = false; //set polled to false every 10 seconds, Sensor device needs to check within 20 seconds in poll()
    Serial.println("10 sec passed");
    digitalClockDisplay();
  } 
}
