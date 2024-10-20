import RPi.GPIO as GPIO
import time
from mfrc522 import SimpleMFRC522

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)

GPIO.setup(20, GPIO.OUT)

module = SimpleMFRC522()

try:
    text = input("Text to be written: ")
    print("Place a tag to write.")
    module.write(text)
    for i in range (1,3):
        GPIO.output(20, 1)
        time.sleep(0.5)
        GPIO.output(20, 0)
    print("Written.")
finally:
    GPIO.cleanup()