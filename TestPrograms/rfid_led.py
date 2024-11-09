import RPi.GPIO as GPIO
from mfrc522 import SimpleMFRC522
import time

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)

GPIO.setup(21,GPIO.OUT)
GPIO.setup(20,GPIO.OUT)
GPIO.setup(16,GPIO.OUT)

END_LOOP = False
RFID_module = SimpleMFRC522()
LED_PIN_TABLE = [21, 20, 16]

try:
    while END_LOOP == False:
        id_RFID, text_RFID = RFID_module.read()
        print("Text: " + text_RFID)
        time.sleep(0.5)

        text_RFID = text_RFID.replace(" ", "")

        if (text_RFID == "LED"):
            for x in LED_PIN_TABLE:
                GPIO.output(x, not GPIO.input(x))

            # for x in LED_PIN_TABLE:
            #     GPIO.output(x, 1)
            # time.sleep(3)
            # for x in LED_PIN_TABLE:
            #     GPIO.output(x, 0)
                
            print("LED changed.")
        if (text_RFID == "END"):
            END_LOOP = True
            for x in LED_PIN_TABLE:
                GPIO.output(x,0)
            print("Ended")
            break
            #GPIO.cleanup()
finally:
    print("Cleanup")
    GPIO.cleanup()
