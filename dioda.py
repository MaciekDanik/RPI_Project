import RPi.GPIO as GPIO
import time

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)
GPIO.setup(40,GPIO.OUT)

for i in range (0,6):
    GPIO.output(40, GPIO.HIGH)
    time.sleep(3)
    GPIO.output(40, GPIO.LOW)
    time.sleep(3)

GPIO.cleanup()