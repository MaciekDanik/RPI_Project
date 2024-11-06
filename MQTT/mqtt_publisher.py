import paho.mqtt.client as mqtt
import adafruit_dht
import board
from time import sleep

broker_address = "192.168.0.69"
broker_port = 1883
topic = "sensor/data"

DHT_PIN = board.D12 #32 #12 bcm
DHT11 = adafruit_dht.DHT11(DHT_PIN)

def read_sensor():
    hum  = DHT11.humidity
    temp = DHT11.temperature

    return hum, temp

def publish_data(client):
    humidity, temperature = read_sensor()

    if humidity is not None and temperature is not None:
        payload = f"{temperature:.2f} {humidity:.2f}"
        client.publish(topic,payload)
        print("Published: {}".format(payload))
    else:
        print("Read error!")


client = mqtt.Client()
client.connect(broker_address, broker_port, 60)

while True:
    publish_data(client)
    sleep(10)