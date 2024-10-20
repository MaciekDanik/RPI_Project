import RPi.GPIO as GPIO
import time

GPIO.setwarnings(False)
#GPIO.setmode(GPIO.BOARD)
GPIO.setmode(GPIO.BCM)
LED_PIN = 20
GPIO.setup(LED_PIN,GPIO.OUT)

for i in range (0,6):
    GPIO.output(LED_PIN, GPIO.HIGH)
    time.sleep(0.5)
    GPIO.output(LED_PIN, GPIO.LOW)
    time.sleep(0.5)

GPIO.cleanup()