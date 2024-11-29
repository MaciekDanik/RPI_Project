import threading #for multithreading
import RPi.GPIO as GPIO #for easy GPIO manipulation
import adafruit_dht #for DHT11 sensor
import board #needed for above library
from time import sleep #to stop the program
from mfrc522 import SimpleMFRC522 #for easy use of the mfrc522 module
from BH1750_light_sensor import BH1750 #needed to use the BH1750 sensor
from datetime import datetime #for current hour reading
import paho.mqtt.client as mqtt #for mqtt comunication
from User import User #User class

GPIO.setwarnings(False) 
GPIO.setmode(GPIO.BCM)

PWM_PIN = 13
GPIO.setup(PWM_PIN, GPIO.OUT) #PWM for fan
pwm = GPIO.PWM(PWM_PIN, 50)



"""RFID variable"""
rfid_text_global = ""

"""User"""
USER_1 = User("USER_1", 370, 550, 65, 25, 5, 23)
USER_2 = User("USER_2", 400, 550, 55, 19, 6, 18)
ACTIVE_USER = USER_1

"""variables needed for dht11 sensor"""
DHT_PIN = board.D12
DHT11 = adafruit_dht.DHT11(DHT_PIN)

"""variables needed for light intesity measures"""
light_sensor = BH1750()
LIGHTS_OFF = False

"""Variable that stores the time at which the blinds will close"""
BLINDS_STATE = 0 # 0- OPEN    1-CLOSED

"""
Variables that hold the pin number for both dc motors and pwm pin
"""
IN1, IN2, IN3, IN4 = 5, 6, 19, 26
FAN_STATE = 0  #0-OFF   1-ON
BASIC_FAN_SPEED = 60 #lower than that will not spin the fan

PIN_TABLE = [16, 20, 21, IN1, IN2, IN3, IN4, PWM_PIN, 23] #Used when ending the system work, for gpio-cleanup

def gpio_setup():
    """
    This function will set up GPIO pins for the whole project.
    """
    GPIO.setup(21, GPIO.OUT) #red LED
    GPIO.setup(20, GPIO.OUT) #yellow LED
    GPIO.setup(16, GPIO.OUT) #red LED

    #window blinds dc motor and cooling fan
    GPIO.setup(IN1, GPIO.OUT) #fan
    GPIO.setup(IN2, GPIO.OUT) #fan
    GPIO.setup(IN3, GPIO.OUT) #DC
    GPIO.setup(IN4, GPIO.OUT) #DC
    GPIO.setup(PWM_PIN, GPIO.OUT) #PWM for fan
    #Buzzer
    GPIO.setup(23, GPIO.OUT)

def rfid_thread():
    """
    This function will handle the RFID comunication between the main thread 
    and the RFID thread. It will alter the ACTIVE_USER based on the RFID tag read by the MFRC522 module.If the text read is END,
    then rfid_text_global variable will be altered.
    """
    RFID_module = SimpleMFRC522()
    global rfid_text_global

    global ACTIVE_USER, USER_1, USER_2
    
    while True:
        _, text_rfid = RFID_module.read()

        buzz(1)
        sleep(0.5)
        text_rfid = text_rfid.replace(" ","")
        buzz(0)

        print(f"Text read: {text_rfid}")

        before_user = ACTIVE_USER.user
        if text_rfid == "USER_1":
            ACTIVE_USER = USER_1
        elif text_rfid == "USER_2":
            ACTIVE_USER = USER_2
        elif text_rfid == "END":
            rfid_text_global = text_rfid
        print(f"Active_USER changed from {before_user} to {ACTIVE_USER.user}")

def mqtt_subscriber():
    """
    This function will hande the user request to change user profiles.
    """
    global ACTIVE_USER, USER_1, USER_2
    broker_addres = "192.168.0.69"
    broker_port = 1883
    topic = "user/preferences"

    def on_message(client, userdata, message):
        global ACTIVE_USER, USER_1, USER_2

        payload = message.payload.decode("utf-8")
        preferences = payload.split(",")
        tmp_user = User("tmp")

        for _ in range(2):
            buzz(1)
            sleep(0.2)
            buzz(0)
            sleep(0.2)

        tmp_user.user = preferences[0]
        tmp_user.LOWER_MARGIN = int(preferences[1])
        tmp_user.UPPER_MARGIN = int(preferences[2])
        tmp_user.ALARM_HUM = int(preferences[3])
        tmp_user.BASE_TEMP = int(preferences[4])
        tmp_user.BLIND_OPEN_TIME = int(preferences[5])
        tmp_user.BLIND_CLOSE_TIME = int(preferences[6])
        tmp_user.NIGHT_TIME_START = int(preferences[7])
        tmp_user.NIGHT_TIME_STOP = int(preferences[8])
        
        if preferences[0] == "USER_1":
            USER_1 = tmp_user
            if ACTIVE_USER.user == "USER_1":
                ACTIVE_USER = USER_1
        elif preferences[0] == "USER_2":
            USER_2 = tmp_user
            if ACTIVE_USER.user == "USER_2":
                ACTIVE_USER = USER_2


    client = mqtt.Client()
    client.on_message = on_message
    client.connect(broker_addres, broker_port)
    client.subscribe(topic)

    print(f"Topic subscribed: {topic}")
    client.loop_forever()


def warning_LED(state):
    """
    This function will turn on or off the yellow LED depending on the 
    state given.
    """
    GPIO.output(20,state)

def buzz(state):
    """
    This function will make the buzzer buzz if passed state is 1 and stop buzzing if state is 0.
    """
    GPIO.output(23, state)

def fan_control(state, dc):
    """
    This function will turn on or off the fan depending on the 
    state given, and control the fan speed depending on the measured temperature.

    state = 1 -> fan ON
    state = 0 -> fan OFF
    dc - duty cycle -> fan speed
    """
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

def spin_motor(direction):
    """
    This function will make the DC motor turn according to the direction passed.
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
    """
    This function will measure light intesity and control the ligting according to user preferences set.
    """
    global LIGHTS_OFF
    now = datetime.now().hour

    if (LIGHTS_OFF == False):
        intensity = int(light_sensor.read_light())
        if (intensity >= 0 and intensity <= ACTIVE_USER.LOWER_MARGIN):
            GPIO.output(21, 1)
            GPIO.output(16, 1)
        elif (intensity > ACTIVE_USER.LOWER_MARGIN and
            intensity <= ACTIVE_USER.UPPER_MARGIN):
            GPIO.output(21, 1)
            GPIO.output(16, 0)
        else:
            GPIO.output(21, 0)
            GPIO.output(16, 0)
    elif LIGHTS_OFF == True:
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
        print(f"\nTemperature: {temperature}*C\tHumidity: {humidity}%")

        if humidity is not None and temperature is not None:
            warning_LED(1)
            sleep(0.5)
            warning_LED(0)

            if humidity >= ACTIVE_USER.ALARM_HUM:
                print(f"Humidity too high: {humidity}%\tTake action!")    
            
            if temperature >= ACTIVE_USER.BASE_TEMP + 1:
                t_diff = temperature - ACTIVE_USER.BASE_TEMP
                dc = min(BASIC_FAN_SPEED + t_diff * 5, 100)

                print(f"t_diff: {t_diff}\tdc: {dc}\n")

                fan_control(1, dc)
            else:
                fan_control(0, BASIC_FAN_SPEED)
    except:
        None


def chek_time():
    """
    This fuction will check:
    *if it is time to close window blinds and act accordingly
    *if it is time to turn lights on or off
    """
    global LIGHTS_OFF
    now = datetime.now().hour
    
    if (now == ACTIVE_USER.BLIND_CLOSE_TIME and BLINDS_STATE == 0):
        blinds_control(1) #close blinds
    elif (now == ACTIVE_USER.BLIND_OPEN_TIME and BLINDS_STATE == 1):
        blinds_control(0) #open blinds

    if (now == ACTIVE_USER.NIGHT_TIME_START and LIGHTS_OFF == False):
        LIGHTS_OFF = True
    elif (now == ACTIVE_USER.NIGHT_TIME_STOP and LIGHTS_OFF == True):
        LIGHTS_OFF = False


if __name__ == "__main__":
    gpio_setup()
    print("Setup - complete!\n")

    RFID_thread = threading.Thread(target=rfid_thread, daemon=True)
    MQTT_thread = threading.Thread(target=mqtt_subscriber, daemon=True)

    RFID_thread.start()
    MQTT_thread.start()
    print("RFID thread and MQTT thread started.\n")

    counter = 0

    try:
        while rfid_text_global != "END":
            light_intensity()
            
            if counter %10 == 0:
                temperature_humidity_control()

            if counter %60 == 0:
                chek_time()

            if counter == 3600:
                counter = 0

            sleep(1)
            counter += 1
    except KeyboardInterrupt:
        pass
    finally:
        for pin in PIN_TABLE:
            GPIO.output(pin, 0)
        for _ in range(3):
            buzz(1)
            sleep(0.2)
            buzz(0)
            sleep(0.2)

        GPIO.cleanup()
