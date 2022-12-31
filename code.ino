#include <ArduinoMqttClient.h>
#include <WiFiNINA.h>
#include <Wire.h>
#include "MAX30105.h"

MAX30105 particleSensor;


///////please enter your sensitive data in the Secret tab/arduino_secrets.h
char ssid[] = "Redmi Note 11T 5G";  // your network SSID (name)
char pass[] = "740ffb9f74dc";       // your network password (use for WPA, or use as key for WEP)

// To connect with SSL/TLS:
// 1) Change WiFiClient to WiFiSSLClient.
// 2) Change port value from 1883 to 8883.
// 3) Change broker value to a server with a known SSL/TLS root certificate
//    flashed in the WiFi module.

WiFiClient wifiClient;
MqttClient mqttClient(wifiClient);

const char broker[] = "broker.mqttdashboard.com";
int port = 1883;
const char topic[] = "ePMS";

long Duration;
int Distance;

int count = 0;

void setup() {
  //Initialize serial and wait for port to open:
  Serial.begin(9600);

  byte ledBrightness = 0x1F;  //Options: 0=Off to 255=50mA
  byte sampleAverage = 8;     //Options: 1, 2, 4, 8, 16, 32
  byte ledMode = 3;           //Options: 1 = Red only, 2 = Red + IR, 3 = Red + IR + Green
  int sampleRate = 100;       //Options: 50, 100, 200, 400, 800, 1000, 1600, 3200
  int pulseWidth = 411;       //Options: 69, 118, 215, 411
  int adcRange = 4096;        //Options: 2048, 4096, 8192, 16384

  particleSensor.setup(ledBrightness, sampleAverage, ledMode, sampleRate, pulseWidth, adcRange);  //Configure sensor with these settings

  //Arduino plotter auto-scales annoyingly. To get around this, pre-populate
  //the plotter with 500 of an average reading from the sensor

  //Take an average of IR readings at power up
  const byte avgAmount = 64;
  long baseValue = 0;
  for (byte x = 0; x < avgAmount; x++) {
    baseValue += particleSensor.getIR();  //Read the IR value
  }
  baseValue /= avgAmount;

  //Pre-populate the plotter so that the Y scale is close to IR values
  for (int x = 0; x < 500; x++)
    Serial.println(baseValue);



  while (!Serial)
    ;  // waits till the Serial Monitor opens up

  // attempt to connect to WiFi network:
  Serial.print("Attempting to connect to WPA SSID: ");
  Serial.println(ssid);
  while (WiFi.begin(ssid, pass) != WL_CONNECTED) {
    // retries till connected
    Serial.print(".");
    delay(2000);
  }

  Serial.println("You're connected to the network");
  Serial.println();

  // You can provide a unique client ID, if not set the library uses Arduino-millis()
  // Each client must have a unique client ID
  // mqttClient.setId("clientId");

  // You can provide a username and password for authentication
  // mqttClient.setUsernamePassword("username", "password");

  Serial.print("Attempting to connect to the MQTT broker: ");
  Serial.println(broker);

  if (!mqttClient.connect(broker, port)) {
    Serial.print("MQTT connection failed! Error code = ");
    Serial.println(mqttClient.connectError());

    while (1)
      ;
  }

  Serial.println("You're connected to the MQTT broker!");
  Serial.println();
}

void loop() {
  // calling poll to send the keep alive message to keep the thing updated and running smoothly
  mqttClient.poll();


  // Prints the following on the Serial Monitor to keep us updated
  Serial.print("Sending message to topic: ");
  Serial.println(topic);
  Serial.print(" ");
  Serial.println(count);

  // sends the message by using the print method
  mqttClient.beginMessage(topic);
  // Change the number for updating the device ID, to distinguish from other devices
  mqttClient.print("Device 1 ");
  float temperature = particleSensor.readTemperatureF();
  mqttClient.print(temperature, 4);

  long irValue = particleSensor.getIR();

  if (checkForBeat(irValue) == true) {
    // We sensed a beat!
    long delta = millis() - lastBeat;
    lastBeat = millis();

    beatsPerMinute = 60 / (delta / 1000.0);

    if (beatsPerMinute < 255 && beatsPerMinute > 20) {
      rates[rateSpot++] = (byte)beatsPerMinute;  // Store this reading in the array
      rateSpot %= RATE_SIZE;                     // Wrap variable

      // Take average of readings
      beatAvg = 0;
      for (byte x = 0; x < RATE_SIZE; x++)
        beatAvg += rates[x];
      beatAvg /= RATE_SIZE;
    }
  } else {
    for (int i = 0; i < 3; i++) {
      digitalWrite(LED_BUILTIN, 1);
      delay(500);
      digitalWrite(LED_BUILTIN, 0);
      delay(500);
    }
  }
  
    mqttClient.print(" ");
    mqttClient.print(beatsPerMinute);
    mqttClient.print(" ");
    mqttClient.println(100*(float)getIR()/(float)getRed());
  
  count++;
  delay(2000);
}
