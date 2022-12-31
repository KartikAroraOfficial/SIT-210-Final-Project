import paho.mqtt.client as mqtt
import time

# Set up the MQTT client
client = mqtt.Client()

# Connect to the MQTT broker
client.connect("broker.mqttdashboard.com", 1883, 60)

# Define the string value to send
string_value = "Device 1 98.2 72 96"
i = 0
while i < 100:
# Publish the string value to the MQTT topic
    client.publish("ePMS", string_value)
    i=i+1
    time.sleep(1)

# Disconnect from the MQTT broker
client.disconnect()