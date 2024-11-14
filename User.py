class User():
    def __init__(self, user, lower=350,
                 upper=500,hum=65, temp=23,
                 open_time=7, close_time=22):
        #tutaj zmienne które teraz są globalne
        self.user = user
        self.LOWER_MARGIN = lower
        self.UPPER_MARGIN = upper
        self.ALARM_HUM = hum
        self.BASE_TEMP = temp
        self.BLIND_OPEN_TIME = open_time
        self.BLIND_CLOSE_TIME = close_time
