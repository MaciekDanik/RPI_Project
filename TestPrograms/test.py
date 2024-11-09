import threading
import RPi.GPIO as GPIO
import adafruit_dht
import board
from time import sleep


GPIO.setwarnings(False) 
GPIO.setmode(GPIO.BCM)

GPIO.setup(21, GPIO.OUT) #red LED
GPIO.setup(20, GPIO.OUT) #yellow LED
GPIO.setup(16, GPIO.OUT) #2x red LED

#tutaj dodać silnik do rolet i wiatrak
IN1, IN2, IN3, IN4, PWM_PIN = 5, 6, 19, 26, 13
GPIO.setup(IN1, GPIO.OUT)
GPIO.setup(IN2, GPIO.OUT)
GPIO.setup(IN3, GPIO.OUT)
GPIO.setup(IN4, GPIO.OUT)
GPIO.setup(PWM_PIN, GPIO.OUT) #PWM for fan

pwm = GPIO.PWM(PWM_PIN, 50)

#Buzzer
GPIO.setup(23, GPIO.OUT)

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


def turn_fan(state, dc):
    """
    state = 1 -> fan ON
    state = 0 -> fan OFF
    """

    if state == 1:
        pwm.start(dc)
    if state == 0:
        pwm.stop()

# GPIO.output(IN1, 1)
# GPIO.output(IN2, 0)
turn_fan(1, 100)
sleep(10)
# GPIO.output(IN1, 0)
# GPIO.output(IN2, 0)
turn_fan(0, 60)


GPIO.cleanup()