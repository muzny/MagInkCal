from datetime import datetime, timedelta

class Day:

    def __init__(self, relative_position: tuple, actual_date: datetime,
                upper_left: tuple, padding: int, width: int):
        self.relative_position = relative_position
        self.actual_date = actual_date
        self.upper_left = upper_left
        self.all_day_events = []
        self.events = []
        self.multiday_events = []
        self.padding = padding
        self.total_width = width
        

    def __str__(self):
        s = "Date: " + str(self.actual_date.date())
        s += "\nrelative position: " + str(self.relative_position) 
        s += "\nupper left: " + str(self.upper_left)
        s += "\nall day events: " + str(self.all_day_events)
        s += "\nevents: " + str(self.events)
        s += "\nmultiday events: " + str(self.multiday_events)
        return s

    def add_allday_event(self, event):
        self.all_day_events.append(event)
        # keep events sorted by time
        self.all_day_events = sorted(self.all_day_events, key = lambda x: x["startDatetime"])

    def add_event(self, event):
        self.events.append(event)
        # keep events sorted by time
        self.events = sorted(self.events, key = lambda x: x["startDatetime"])

    def add_multiday_event(self, event):
        self.multiday_events.append(event)
        # keep events sorted by time
        self.multiday_events = sorted(self.multiday_events, key = lambda x: x["startDatetime"])

    # def 