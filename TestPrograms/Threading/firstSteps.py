import threading
from time import sleep

def square(list):
    for num in list:
        print("Square: {}".format(num*num))
        sleep(1)

def cube(list):
    for num in list:
        print("Cube: {}".format(num*num*num))
        sleep(2)

        
if __name__ == "__main__":
    nums = [1,2,3,4,5]

    t1 = threading.Thread(target=square, args=(nums,))
    t2 = threading.Thread(target=cube, args=(nums,))

    t1.start()
    t2.start()

    t1.join()
    t2.join()