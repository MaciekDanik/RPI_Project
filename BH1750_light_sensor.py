import time
import smbus
import RPi.GPIO as GPIO

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)

BH1750_ADDR = 0x23 #sensor adress on the i2c bus
CMD_READ = 0x11 #comand to read light sensitivity

class BH1750(object):

   def __init__(self):
       # Rev 2 of Raspberry Pi and all newer use bus 1
       self.bus = smbus.SMBus(1)

   def read_light(self):
       data = self.bus.read_i2c_block_data(BH1750_ADDR, CMD_READ)
       result = (data[1] + (256 * data[0])) / 1.2
       return format(result,'.0f') 
   
   def print_result(self):
        try:
            print("Light: " + self.read_light() + " Lux")
        except FileNotFoundError:
            print('ERROR: Please enable I2C.')
        except OSError:
            print('ERROR: I2C device not found. Please check BH1750 wiring.')
        except:
            print('ERROR: General unknown error')

obj = BH1750()
for i in range (1, 20):
    obj.print_result()
    time.sleep(1)