import adafruit_dht
import RPi.GPIO as GPIO
import time
import board

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(21,GPIO.OUT)
GPIO.setup(16,GPIO.OUT)

DHT_PIN = board.D12 #32 #12 bcm
DHT11 = adafruit_dht.DHT11(DHT_PIN)
ALARM_HUM = 55

#/usr/local/lib/python3.12/dist-packages/board.py'

for i in range (1,60):
    try:
        temperature = DHT11.temperature
        humidity = DHT11.humidity
        if humidity is not None and temperature is not None:
            GPIO.output(21, GPIO.HIGH)
            print(str(i) + " Temp: " + str(temperature) + "*C Hum: " + str(humidity)+"%")
            time.sleep(0.5)
            GPIO.output(21, GPIO.LOW)

            if humidity >= ALARM_HUM:
                GPIO.output(16, GPIO.HIGH)
                print("Humidity too high!!! Take action.")
            else:
                GPIO.output(16,GPIO.LOW)
        else:
            print("Sensor failure. Check wiring.")
        time.sleep(9.5)

    except:
        continue

