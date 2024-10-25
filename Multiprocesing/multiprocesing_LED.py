import multiprocessing
import RPi.GPIO as GPIO
from time import sleep

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)

GPIO.setup(21,GPIO.OUT)
GPIO.setup(20,GPIO.OUT)
GPIO.setup(16,GPIO.OUT)

LED_PIN = [16, 20, 21]

def blink(conn):
    while True:
        glitch_msg = conn.recv()
        for led in LED_PIN:
            if glitch_msg == "YES":
                GPIO.output(16,1)
                GPIO.output(21,1)
                GPIO.output(20,0)
            elif glitch_msg == "NO":
                # GPIO.output(led, not GPIO.input(led))
                GPIO.output(16,0)
                GPIO.output(21,0)
                GPIO.output(20,1)

def glitch(conn):
    ctr = 0
    while True:
        if ctr%2 == 0:
            conn.send("YES")
        else:
            conn.send("NO")
        ctr += 1
        sleep(1)
        


if __name__ =="__main__":
    blink_conn, glitch_conn = multiprocessing.Pipe()

    p1 = multiprocessing.Process(target=blink, args=(blink_conn,))
    p2 = multiprocessing.Process(target=glitch, args=(glitch_conn,))

    try:
        p1.start()
        p2.start()
    except KeyboardInterrupt:
        for led in LED_PIN:
            GPIO.output(led,0)
        GPIO.cleanup()
        print("Cleanup")

        p1.join()
        p2.join()
