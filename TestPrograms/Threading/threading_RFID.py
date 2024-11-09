import threading
import RPi.GPIO as GPIO
from time import sleep
from mfrc522 import SimpleMFRC522

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)

GPIO.setup(21,GPIO.OUT)
GPIO.setup(20,GPIO.OUT)
GPIO.setup(16,GPIO.OUT)

LED_PIN_TABLE = [16, 20, 21]
rfid_text = ""

def rfid_thread():
    RFID_module = SimpleMFRC522()
    END_LOOP = False
    global rfid_text
    while END_LOOP == False:
        id_RFID, text_RFID = RFID_module.read()
        sleep(0.5)
        text_RFID = text_RFID.replace(" ","")
        print("Text read: {}".format(text_RFID))

        if text_RFID == "END":
            END_LOOP = True
        
        rfid_text = text_RFID


if __name__ == "__main__":
    END_LOOP = False

    RFID_thread = threading.Thread(target=rfid_thread, daemon=True)
    RFID_thread.start()
    
    while END_LOOP == False:
        if rfid_text == "LED":
            # for led in LED_PIN_TABLE:
            #     GPIO.output(led, not GPIO.input(led))
            GPIO.output(21, not GPIO.input(21))
            GPIO.output(16, not GPIO.input(16))
            print("LED changed.")
            rfid_text = ""
        elif rfid_text == "END":
            END_LOOP = True
            for led in LED_PIN_TABLE:
                GPIO.output(led,0)
            rfid_text = ""
            print("Ended.")
        GPIO.output(20, not GPIO.input(20))
        sleep(1)
    
    GPIO.cleanup()