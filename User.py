class User():
    def __init__(self, user, lower=350,
                 upper=500,hum=65, temp=23,
                 open_time=7, close_time=22,
                 night_start=23, night_stop=8):
        self.user = user
        self.LOWER_MARGIN = lower
        self.UPPER_MARGIN = upper
        self.ALARM_HUM = hum
        self.BASE_TEMP = temp
        self.BLIND_OPEN_TIME = open_time
        self.BLIND_CLOSE_TIME = close_time
        self.NIGHT_TIME_START = night_start
        self.NIGHT_TIME_STOP = night_stop
