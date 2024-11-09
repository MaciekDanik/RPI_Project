import RPi.GPIO as GPIO
from mfrc522 import SimpleMFRC522
from BH1750_light_sensor import BH1750
import time

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)

GPIO.setup(21,GPIO.OUT)
GPIO.setup(20,GPIO.OUT)
GPIO.setup(16,GPIO.OUT)

END_LOOP = False
RFID_module = SimpleMFRC522()
light_sensor = BH1750()
LED_PIN_TABLE = [21, 20, 16]

def measureLight():
    lux = int(light_sensor.read_light())

    if lux < 500:
        GPIO.output(20,1)
    else:
        GPIO.output(20,0)

def rfidControl():
    id_RFID, text_RFID = RFID_module.read()
    print("Text: " + text_RFID)
    time.sleep(0.5)

    text_RFID = text_RFID.replace(" ", "")

    if (text_RFID == "LED"):
        GPIO.output(21, not GPIO.input(21))
            
        print("LED changed.")

    if (text_RFID == "END"):
        END_LOOP = True
        for x in LED_PIN_TABLE:
            GPIO.output(x,0)
        print("Ended")

try:
    while END_LOOP == False:
        measureLight()

        rfidControl()
finally:
    print("Cleanup")
    GPIO.cleanup()
