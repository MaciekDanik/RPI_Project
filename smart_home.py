import threading
import RPi.GPIO as GPIO
import adafruit_dht
import board
from time import sleep
from mfrc522 import SimpleMFRC522
from BH1750_light_sensor import BH1750
from datetime import datetime
import paho.mqtt.client as mqtt
from User import User

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
ACTIVE_USER = User("USER_0")

"""variables needed for dht11 sensor"""
DHT_PIN = board.D12
DHT11 = adafruit_dht.DHT11(DHT_PIN)

"""variables needed for light intesity measures"""
light_sensor = BH1750()

"""Variable that stores the time at which the blinds will close"""
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

    global ACTIVE_USER, USER_1, USER_2
    
    while True:
        _, text_rfid = RFID_module.read()
        buzz(1)
        sleep(0.5)

        text_rfid = text_rfid.replace(" ","")
        buzz(0)

        print("Text read: {}".format(text_rfid))

        #zrobic klasę user i subscriber mqtt odbiera dane, i 
        #podmienia je w globalnej zmiennej. Do tego publisher mqtt
        #wysyła dane jako pakiet. osobny wątek odbiera i podmienia dane w globalnym user

        print("Active user before: {}".format(ACTIVE_USER.user))
        if text_rfid == "USER_1":
            ACTIVE_USER = USER_1
        elif text_rfid == "USER_2":
            ACTIVE_USER = USER_2
        elif text_rfid == "END":
            rfid_text_global = text_rfid
        print("Active user after: {}".format(ACTIVE_USER.user))

def mqtt_subscriber():
    global ACTIVE_USER, USER_1, USER_2
    broker_addres = "192.168.0.69"
    broker_port = 1883
    topic = "user/preferences"

    def on_message(client, userdata, message):
        global ACTIVE_USER, USER_1, USER_2

        payload = message.payload.decode("utf-8")
        # preferences = map(str, payload.split(","))
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
        tmp_user.BASE_TEMP = int(preferences[3])
        tmp_user.BLIND_OPEN_TIME = int(preferences[4])
        tmp_user.BLIND_CLOSE_TIME = int(preferences[5])
        
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

    print("Topic subscribed: {}".format(topic))
    client.loop_forever()


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

def temperature_humidity_control():
    """
    This function will read temperature and humidity and control the fan 
    according to the reading.
    """
    try:
        temperature = DHT11.temperature
        humidity = DHT11.humidity
        print("\nTemperature: {}\tHumidity: {}".format(temperature, humidity))

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
            
            if temperature >= ACTIVE_USER.BASE_TEMP + 1:
                t_diff = temperature - ACTIVE_USER.BASE_TEMP
                dc = min(BASIC_FAN_SPEED + t_diff * 5, 100)

                print("t_diff: {}\tdc: {}\n".format(t_diff, dc))

                fan_control(1, dc)
            else:
                fan_control(0, BASIC_FAN_SPEED)
    except:
        None


def chek_blinds_time():
    now = datetime.now().hour
    
    if (now == ACTIVE_USER.BLIND_CLOSE_TIME and
            BLINDS_STATE == 0):
        blinds_control(1) #close blinds
    elif (now == ACTIVE_USER.BLIND_OPEN_TIME and
            BLINDS_STATE == 1):
        blinds_control(0) #open blinds

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
            # print("Light measured")

            chek_blinds_time()
            # print("Blinds closing time chcecked")

            # blinds_control(1) # for test purposes
            
            #częstość pomiaru temperatury? też jako zmienna USER.coś
            if counter %10 == 0:
                temperature_humidity_control()

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



    
