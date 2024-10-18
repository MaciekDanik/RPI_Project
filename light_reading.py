import RPi.GPIO as GPIO
import time
from BH1750_light_sensor import BH1750

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)

#konfiguracja pinów do obsługi diód led
GPIO.setup(40,GPIO.OUT) #jedna dioda
GPIO.setup(36,GPIO.OUT) #dwie diody

sensor = BH1750()

for i in range (1,25):
    intensity = int(sensor.read_light())
    #print("Intensity is: " + intensity + " Lux.")

    if (intensity >= 0 and intensity <= 350):
        #tutaj uruchom dwie diody
        print("dwie")
        GPIO.output(40, GPIO.HIGH)
        GPIO.output(36, GPIO.HIGH)
    elif (intensity > 350 and intensity <= 500):
        #tylko jedna dioda
        print("jedna")
        GPIO.output(36, GPIO.LOW)
        GPIO.output(40, GPIO.HIGH)
    else:
        #wyłącz diody
        print("zadna")
        GPIO.output(40, GPIO.LOW)
        GPIO.output(36, GPIO.LOW)

    time.sleep(1)

GPIO.cleanup()