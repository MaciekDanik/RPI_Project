import paho.mqtt.client as mqtt
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

broker_address = "192.168.0.69"
broker_port = 1883
topic = "sensor/data"

def on_message(client, userdata, message):
    payload = message.payload.decode("utf-8")
    temp, hum = map(float, payload.split(" "))
    print("Temp: {}  Hum: {}".format(temp, hum))

client = mqtt.Client()
client.on_message = on_message
client.connect(broker_address, broker_port)
client.subscribe(topic)

print("Topic subscription '{}' on broker {}:{}".format(topic, broker_address, broker_port))
client.loop_forever()
