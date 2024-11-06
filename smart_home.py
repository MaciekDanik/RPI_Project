import threading
import RPi.GPIO as GPIO
import adafruit_dht
import board
from time import sleep
from mfrc522 import SimpleMFRC522
from BH1750_light_sensor import BH1750
from datetime import datetime

def gpio_setup():
    """
    This function will set up GPIO pins for the whole project.
    """
    GPIO.setwarnings(False) 
    GPIO.setmode(GPIO.BCM)

    GPIO.setup(21, GPIO.OUT) #red LED
    GPIO.setup(20, GPIO.OUT) #yellow LED
    GPIO.setup(16, GPIO.OUT) #2x red LED

    #tutaj dodać silnik do rolet i wiatrak
    GPIO.setup(5, GPIO.OUT) #IN1
    GPIO.setup(6, GPIO.OUT) #IN2
    GPIO.setup(19, GPIO.OUT) #IN3
    GPIO.setup(26, GPIO.OUT) #IN4

    #Buzzer
    GPIO.setup(23, GPIO.OUT)

def rfid_thread():
    """
    This function will handle the RFID comunication between the main thread 
    and the RFID thread. It will alter the RFID_TEXT variable after it 
    reads a tag.
    """
    RFID_module = SimpleMFRC522()
    global rfid_text_global
    global ALARM_TEMP

    while True:
        id_rfid, text_rfid = RFID_module.read()
        buzz(1)
        sleep(0.5)

        text_rfid = text_rfid.replace(" ","")
        buzz(0)


        print("Text read: {}".format(text_rfid))

        if text_rfid == "HOT":
            ALARM_TEMP = 25
        elif text_rfid == "COLD":
            ALARM_TEMP = 21
        elif text_rfid == "END":
            rfid_text_global = text_rfid

def warning_LED(state):
    """
    This function will turn on or off the yellow LED depending on the 
    state given.
    """
    GPIO.output(20,state)

def buzz(state):
    GPIO.output(23, state)

def fan_control(state):
    """
    This function will turn on or off the fan depending on the 
    state given.
    """
    #fan
    if state == 1:
        GPIO.output(19, 1)
        GPIO.output(26, 0)
    elif state == 0:
        GPIO.output(19, 0)
        GPIO.output(26, 1)

def blinds_control(state):
    """
    This function will turn the dc motor responsible for opening and closing the blinds depending on state passed.
    1 - open
    0 - close
    """
    global BLINDS_STATE

    if state == 1:
        GPIO.output(5, 1)
        GPIO.output(6, 0)
        sleep(5)
        GPIO.output(5, 0)
        GPIO.output(6, 0)
        BLINDS_STATE = "CLOSED"

        print("Blinds closed")
    elif state == 0:
        GPIO.output(5, 0)
        GPIO.output(6, 1)
        sleep(7)
        GPIO.output(5, 0)
        GPIO.output(6, 0)
        BLINDS_STATE = "OPEN"

        print("Blinds open")
    

def light_intensity():
    global light_sensor, LOWER_MARGIN, HIGHER_MARGIN

    intensity = int(light_sensor.read_light())

    if (intensity >= 0 and intensity <= LOWER_MARGIN):
        GPIO.output(21, 1)
        GPIO.output(16, 1)
    elif (intensity > LOWER_MARGIN and intensity <= HIGHER_MARGIN):
        GPIO.output(21, 1)
        GPIO.output(16, 0)
    else:
        GPIO.output(21, 0)
        GPIO.output(16, 0)

def temperature_humidity_control():
    """
    This function will read temperature and humidity and control the fan 
    according to the reading.
    """
    try:
        temperature = DHT11.temperature
        humidity = DHT11.humidity

        if humidity is not None and temperature is not None:
            warning_LED(1)
            sleep(0.5)
            warning_LED(0)

            if humidity >= ALARM_HUM:
                fan_control(1)
                print("Humidity too high!")
                print("Fan turned on.")
            else:
                fan_control(0)
                print("Fan turned off.")
            
            if temperature >= ALARM_TEMP:
                fan_control(1)
                print("Temperature higher than preset!")
                print("Fan turned on.")
            else:
                fan_control(0)
                print("Fan turned off.")
    except:
        None


def chek_blinds_time():
    global BLIND_CLOSE_TIME, BLINDS_STATE

    now = datetime.now().hour
    

    if now >=  BLIND_CLOSE_TIME and BLINDS_STATE == "OPEN":
        blinds_control(1) #close blinds
    elif now < BLIND_CLOSE_TIME and BLINDS_STATE == "CLOSED":
        blinds_control(0) #open blinds

if __name__ == "__main__":

    """RFID variable"""
    rfid_text_global = ""

    """variables needed for dht11 sensor"""
    DHT_PIN = board.D12
    DHT11 = adafruit_dht.DHT11(DHT_PIN)
    ALARM_HUM = 65
    ALARM_TEMP = 26

    """variables needed for light intesity measures"""
    light_sensor = BH1750()
    LOWER_MARGIN = 350
    HIGHER_MARGIN = 500

    """Variable that stores the time at which the blinds will close"""
    BLIND_CLOSE_TIME = 21
    BLINDS_STATE = "OPEN"


    RFID_thread = threading.Thread(target=rfid_thread, daemon=True)
    RFID_thread.start()

    counter = 0

    try:
        gpio_setup()

        while rfid_text_global != "END":
            light_intensity()
            chek_blinds_time()

            # blinds_control(1) # for test purposes
            
            if counter %10 == 0:
                temperature_humidity_control()

            sleep(1)
            counter += 1
    except KeyboardInterrupt:
        pass
    finally:
        l = [16, 20, 21]
        for i in l:
            GPIO.output(i, 0)

        GPIO.cleanup()



    