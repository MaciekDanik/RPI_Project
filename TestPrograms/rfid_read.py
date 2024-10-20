import RPi.GPIO as GPIO
import time
from mfrc522 import SimpleMFRC522

module = SimpleMFRC522()

try:
    id, text = module.read()
    print("ID: " + str(id))
    print("Text: " + text)
finally:
    GPIO.cleanup()