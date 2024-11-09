import threading
import RPi.GPIO as GPIO
import adafruit_dht
import board
from time import sleep
from mfrc522 import SimpleMFRC522
from BH1750_light_sensor import BH1750
from datetime import datetime

GPIO.setwarnings(False) 
GPIO.setmode(GPIO.BCM)

PWM_PIN = 13
GPIO.setup(PWM_PIN, GPIO.OUT) #PWM for fan
pwm = GPIO.PWM(PWM_PIN, 50)


"""RFID variable"""
rfid_text_global = ""

"""variables needed for dht11 sensor"""
DHT_PIN = board.D12
DHT11 = adafruit_dht.DHT11(DHT_PIN)
ALARM_HUM = 65
BASE_TEMP = 19

"""variables needed for light intesity measures"""
light_sensor = BH1750()
LOWER_MARGIN = 350
UPPER_MARGIN = 500

"""Variable that stores the time at which the blinds will close"""
BLIND_CLOSE_TIME = 0
BLIND_OPEN_TIME = 23 #<-for tests should be 7
BLINDS_STATE = 0 # 0- OPEN    1-CLOSED

"""
Variables that hold the pin number for both dc motors and pwm pin
"""
IN1, IN2, IN3, IN4 = 5, 6, 19, 26
FAN_STATE = 0  #0-OFF   1-ON
BASIC_FAN_SPEED = 60

PIN_TABLE = [16, 20, 21, IN1, IN2, IN3, IN4, PWM_PIN, 23]

def gpio_setup():
    """
    This function will set up GPIO pins for the whole project.
    """
    GPIO.setup(21, GPIO.OUT) #red LED
    GPIO.setup(20, GPIO.OUT) #yellow LED
    GPIO.setup(16, GPIO.OUT) #red LED

    #window blinds dc motor and cooling fan
    GPIO.setup(IN1, GPIO.OUT)
    GPIO.setup(IN2, GPIO.OUT)
    GPIO.setup(IN3, GPIO.OUT)
    GPIO.setup(IN4, GPIO.OUT)
    GPIO.setup(PWM_PIN, GPIO.OUT) #PWM for fan
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
    global BASE_TEMP, ALARM_HUM, LOWER_MARGIN, UPPER_MARGIN, BLIND_CLOSE_TIME, BLIND_OPEN_TIME

    while True:
        id_rfid, text_rfid = RFID_module.read()
        buzz(1)
        sleep(0.5)

        text_rfid = text_rfid.replace(" ","")
        buzz(0)


        print("Text read: {}".format(text_rfid))

        if text_rfid == "USER1":
            BASE_TEMP = 22
            ALARM_HUM = 65
            LOWER_MARGIN = 350
            UPPER_MARGIN = 500
            BLIND_CLOSE_TIME = 22
            BLIND_OPEN_TIME = 7
        elif text_rfid == "USER2":
            BASE_TEMP = 19
            ALARM_HUM = 55
            LOWER_MARGIN = 400
            UPPER_MARGIN = 550
            BLIND_CLOSE_TIME = 23
            BLIND_OPEN_TIME = 6
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

def fan_control(state, dc):
    """
    This function will turn on or off the fan depending on the 
    state given, and control the fan speed depending on the measured temperature.

    state = 1 -> fan ON
    state = 0 -> fan OFF
    dc - duty cycle -> fan speed
    """
    # global pwm
    global FAN_STATE

    if state == 1 and FAN_STATE == 0:
        pwm.start(dc)
        FAN_STATE = 1
        print("Fan turned ON.")
    elif state == 1 and FAN_STATE == 1:
        pwm.ChangeDutyCycle(dc)

    if state == 0 and FAN_STATE == 1:
        pwm.stop()
        FAN_STATE = 0
        print("Fan turned OFF.")
    
    # if state == 1:
    #     GPIO.output(IN3, 1)
    #     GPIO.output(IN4, 0)
    # elif state == 0:
    #     GPIO.output(IN3, 0)
    #     GPIO.output(IN4, 1)

def spin_motor(direction):
    """
    direction = 1 -> turn right
    direction = -1 -> turn left
    direction = 0 -> stop turning
    """
    if direction == 1:
        GPIO.output(IN3, 1)
        GPIO.output(IN4, 0)
    elif direction == -1:
        GPIO.output(IN3, 0)
        GPIO.output(IN4, 1)
        print(GPIO.input(IN2))
    elif direction == 0:
        GPIO.output(IN3, 0)
        GPIO.output(IN4, 0)
    else:
        for i in range (2):
            GPIO.output(20, not GPIO.input(20))
            sleep(0.25)

def blinds_control(state):
    """
    This function will turn the dc motor responsible for opening and closing the blinds depending on state passed.
    1 - open
    0 - close
    """
    global BLINDS_STATE

    if state == 1:
        spin_motor(1)
        sleep(5)
        spin_motor(0)
        BLINDS_STATE = 1

        print("Blinds closed")
    elif state == 0:
        spin_motor(-1)
        sleep(7)
        spin_motor(0)
        BLINDS_STATE = 0

        print("Blinds open")
    

def light_intensity():
    intensity = int(light_sensor.read_light())

    if (intensity >= 0 and intensity <= LOWER_MARGIN):
        GPIO.output(21, 1)
        GPIO.output(16, 1)
    elif (intensity > LOWER_MARGIN and intensity <= UPPER_MARGIN):
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
        print("Temperature: {}\tHumidity: {}".format(temperature, humidity))

        if humidity is not None and temperature is not None:
            warning_LED(1)
            sleep(0.5)
            warning_LED(0)

            # if humidity >= ALARM_HUM:
            #     fan_control(1)
            #     print("Humidity too high!")
            #     print("Fan turned on.")
            # else:
            #     fan_control(0)
            #     print("Fan turned off.")
            
            if temperature >= BASE_TEMP + 1:
                t_diff = temperature - BASE_TEMP
                dc = min(BASIC_FAN_SPEED + t_diff * 5, 100)

                print("t_diff: {}\tdc: {}".format(t_diff, dc))

                fan_control(1, dc)
            else:
                fan_control(0, BASIC_FAN_SPEED)
    except:
        None


def chek_blinds_time():
    now = datetime.now().hour
    

    if now ==  BLIND_CLOSE_TIME and BLINDS_STATE == 0:
        blinds_control(1) #close blinds
    elif now == BLIND_OPEN_TIME and BLINDS_STATE == 1:
        blinds_control(0) #open blinds

if __name__ == "__main__":
    gpio_setup()
    print("Setup - complete!")

    RFID_thread = threading.Thread(target=rfid_thread, daemon=True)
    RFID_thread.start()
    print("RFID thread started")

    # pwm = GPIO.PWM(PWM_PIN, 50)

    counter = 0

    try:
        while rfid_text_global != "END":
            light_intensity()
            # print("Light measured")

            chek_blinds_time()
            # print("Blinds closing time chcecked")

            # blinds_control(1) # for test purposes
            
            if counter %10 == 0:
                temperature_humidity_control()

            sleep(1)
            counter += 1
    except KeyboardInterrupt:
        pass
    finally:
        for pin in PIN_TABLE:
            GPIO.output(pin, 0)

        GPIO.cleanup()



    