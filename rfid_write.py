import RPi.GPIO as GPIO
import time
from mfrc522 import SimpleMFRC522

module = SimpleMFRC522()

try:
    text = input("Text to be written: ")
    print("Place a tag to write.")
    module.write(text)
    print("Written.")
finally:
    GPIO.cleanup()