import RPi.GPIO as GPIO
import time

def buzz(state):
    GPIO.output(23, state)

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
LED_PINS = [20, 21, 16]

GPIO.setup(23, GPIO.OUT)

for pin in LED_PINS:
    GPIO.setup(pin,GPIO.OUT)

for i in range (0,5):
    for led in LED_PINS:
        GPIO.output(led, 1)
        buzz(1)
        time.sleep(0.5)
        GPIO.output(led, 0)
        buzz(0)
        time.sleep(0.5)

GPIO.cleanup()