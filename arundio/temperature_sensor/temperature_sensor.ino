#include <ESP8266WiFi.h>
#include <WiFiClient.h>
#include <ESP8266WebServer.h>
#include <ESP8266mDNS.h>

#include <OneWire.h>
#include <DallasTemperature.h>
#include <ESP8266WiFi.h>

#ifndef STASSID
#define STASSID "WIFI SSID"
#define STAPSK  "WIFI PASSWORD"
#endif

#define ONE_WIRE_BUS D4
OneWire oneWire(ONE_WIRE_BUS);
DallasTemperature DS18B20(&oneWire);

const char* ssid = STASSID;
const char* password = STAPSK;

const int relayPin = D0;
void ron(){  digitalWrite(relayPin, LOW); Serial.println("on");}
void roff(){  digitalWrite(relayPin, HIGH); Serial.println("off");}


ESP8266WebServer server(80);

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

void setup(void) {
  pinMode(relayPin, OUTPUT); 
  roff();
  
  Serial.begin(115200);
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
  server.on("/temp", temp);
  
  server.onNotFound(handleNotFound);
  server.begin();
  Serial.println("HTTP server started");
}

  void temp(){
    DS18B20.requestTemperatures();
    float tempC = DS18B20.getTempCByIndex(0);
    if(tempC == DEVICE_DISCONNECTED_C){
      Serial.println("error no device");
    }
    else{
      char str[20];
      sprintf(str, "%f", tempC);
      server.send(200, "text/plain", str);
    }
    delay(1000);
  }


void loop(void) {
  server.handleClient();
  MDNS.update();
}
