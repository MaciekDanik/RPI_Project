import multiprocessing
import RPi.GPIO as GPIO
from mfrc522 import SimpleMFRC522
from time import sleep
from ctypes import c_bool

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)

GPIO.setup(21,GPIO.OUT)
GPIO.setup(20,GPIO.OUT)
GPIO.setup(16,GPIO.OUT)

LED_PIN_TABLE = [21, 20, 16]

def sender(conn):
    RFID_module = SimpleMFRC522()
    END_LOOP = False
    while END_LOOP == False:
        print("Sender.")
        try:
            id_RFID, text_RFID = RFID_module.read()
            sleep(0.5)
            text_RFID = text_RFID.replace(" ", "")

            if text_RFID == "END": 
                END_LOOP = True

            conn.send(text_RFID)
            print("Sent the msg: {}".format(text_RFID))
        except:
            print("Some error occured.")

def reciver(conn, END_LOOP_GLOBAL):
    END_LOOP = False
    ctr = 0
    while END_LOOP == False:
        print(ctr)
        msg = conn.recv()
        print("Msg: {}".format(msg))
        
        if msg == "LED":
            for led in LED_PIN_TABLE:
                GPIO.output(led, not GPIO.input(led))
            print("LED changed.")
        elif msg == "END":
            END_LOOP = True
            END_LOOP_GLOBAL.value = True
            for led in LED_PIN_TABLE:
                GPIO.output(led, 0)
            print("Ended.")
            break
        else:
            print("Unknown msg.")
        ctr += 1

if __name__ == "__main__":
    END_LOOP_Global = multiprocessing.Value(c_bool, False)

    sender_conn, reciver_conn = multiprocessing.Pipe()
    p1 = multiprocessing.Process(target=sender, args=(sender_conn,), daemon=True)
    p2 = multiprocessing.Process(target=reciver, args=(reciver_conn,END_LOOP_Global), daemon=True)

    #while END_LOOP_Global.value == False:
    try:
        p1.start()
        print("P1 start.")
        sleep(0.2)
        p2.start()
        print("P2 start.")
        sleep(0.2)
    finally:
        for led in LED_PIN_TABLE:
            GPIO.output(led,0)

    p1.join()
    print("P2 join.")
    p2.join()
    print("P2 join.")

    GPIO.cleanup()
    print("Cleanup")

