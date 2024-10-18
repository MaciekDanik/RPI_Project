import RPi.GPIO as GPIO
import time

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)

GPIO.setup(16,GPIO.OUT)
GPIO.setup(21,GPIO.OUT)

for i in range (1,10):
    GPIO.output(16, GPIO.HIGH)
    time.sleep(0.5)
    GPIO.output(16, GPIO.LOW)
    time.sleep(0.5)

GPIO.cleanup()

print("CleanUP succesfull!")