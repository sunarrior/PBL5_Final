import datetime

class TimeUsing:
    def __init__(self, timeStart, timeEnd, seconds):
        self.timeStart = timeStart
        self.timeEnd = timeEnd
        self.seconds = seconds
    def setSeconds(self):
        date_format = "%H:%M:%S %d/%m/%Y"
        time_on = datetime.datetime.strptime(self.timeStart,date_format)
        time_off = datetime.datetime.strptime(self.timeEnd,date_format)
        self.seconds = int((time_off - time_on).seconds)
