import multiprocessing
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

    proc1 = multiprocessing.Process(target=square, args=(nums,))
    proc2 = multiprocessing.Process(target=cube, args=(nums,))

    proc1.start()
    proc2.start()

    proc1.join()
    proc2.join()