#pin 32 output z dht11
import adafruit_dht
import RPi.GPIO as GPIO
import time
import board

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(21,GPIO.OUT)

#/usr/local/lib/python3.12/dist-packages/board.py'

DHT_PIN = board.D12#32 #12 bcm
DHT11 = adafruit_dht.DHT11(DHT_PIN)


for i in range (1,100):
    try:
        temperature = DHT11.temperature
        humidity = DHT11.humidity
        if humidity is not None and temperature is not None:
            GPIO.output(21, GPIO.HIGH)
            print(str(i) + " Temp: " + str(temperature) + "*C Hum: " + str(humidity)+"%")
        else:
            print("Sensor failure. Check wiring.")
        time.sleep(10)
        GPIO.output(21, GPIO.LOW)

    except:
        continue

