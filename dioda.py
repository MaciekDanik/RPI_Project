import RPi.GPIO as GPIO
import time

GPIO.setwarnings(False)
#GPIO.setmode(GPIO.BOARD)
GPIO.setmode(GPIO.BCM)
GPIO.setup(21,GPIO.OUT)

for i in range (0,6):
    GPIO.output(21, GPIO.HIGH)
    time.sleep(0.5)
    GPIO.output(21, GPIO.LOW)
    time.sleep(0.5)

GPIO.cleanup()