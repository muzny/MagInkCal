from PIL import ImageDraw, ImageFont, Image
from datetime import datetime, timedelta
import calendar as cal
import pickle
from day import Day


# in pixels
MARGINS = 10
PADDING = 10
FIRST_DAY = 6 # start weeks on Sundays
NUM_WEEKS_DISPLAY = 2
NUM_DAYS_IN_WEEK = 7
HEADER_SPACE = 50
EVENT_HEIGHT = 5 * PADDING

class PictureHelper:

    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.start_x = MARGINS
        self.end_x = self.width - (2 * MARGINS)
        # allow room for month and day names at the top
        self.start_y = MARGINS + HEADER_SPACE
        self.end_y = self.height - (2 * MARGINS)
        self.first_day = FIRST_DAY
        self.day_starts = {}
        self.day_width = (self.end_x - self.start_x) // NUM_DAYS_IN_WEEK
        self.day_height = (self.end_y - self.start_y) // NUM_WEEKS_DISPLAY
        
        for i in range(NUM_DAYS_IN_WEEK):
            relative_day = (i + 1) % NUM_DAYS_IN_WEEK
            day_start_x = self.start_x + relative_day * self.day_width
            for week_num in range(NUM_WEEKS_DISPLAY):
                week_start_y = self.start_y + week_num * self.day_height
                self.day_starts[(week_num, i)] = (day_start_x, week_start_y)
        print(self.day_starts)

    def get_date_area(self, week_num: int, day_num: int):
        """
        Gets the pixel value for the upper left corner of 
        this week/day's relative position
        week_num is 0 or 1
        day_num is 0 - 6, 0 is MONDAY, 6 is SUNDAY

        Parameters:
            week_num (int): 0 or 1 for the first or second week in the
            display
            day_num (int): 0 through 6, 0 is MONDAY, 6 is SUNDAY

        Return: tuple of (x, y) coordinates
        """
        relative_day = (day_num + 1) % NUM_DAYS_IN_WEEK
        return self.day_starts[(week_num, relative_day)]

    def render(self, start_day_num, start_month_num, start_year_num):
        """
        Draws the actual picture that is width by height

        Parameters:
            start_day_num (int): 1 - 31, for the date of the first
            day to be displayed in the picture
            start_month_num (int): 1 - 12, for the month that contains
            the first day in the display
        """
        day_before = start_day_num - 1
        # blank canvas
        plane = Image.new('1', (self.width, self.height), 255)
        # start with just the lines
        draw = ImageDraw.Draw(plane)

        for i in range(0, NUM_DAYS_IN_WEEK + 1):
            start = (self.start_x + i * self.day_width, self.start_y)
            end = (self.start_x + i * self.day_width, self.start_y + 2 * self.day_height)
            draw.line([start, end], fill = 0, width = 3)
        
        for i in range(0, NUM_WEEKS_DISPLAY + 1):
            start = (self.start_x, self.start_y + i * self.day_height)
            end = (self.start_x + 7 * self.day_width, self.start_y + i * self.day_height)
            draw.line([start, end], fill = 0, width = 3)

        # get number of days in the target month
        month_end_day_of_week, days_in_month = cal.monthrange(start_year_num, start_month_num)


        # add numbers
        # (0, 6) is the first day of the first week
        # (1, 6) is the first day of the second week

        # and create mapping of dates (day, month, year) to relative dates
        self.dates_to_relative_days = {}
        self.dates_to_day_objs = {}

        font = ImageFont.load_default()
        start_date = datetime(start_year_num, start_month_num, start_day_num)

        current_date = datetime(start_year_num, start_month_num, start_day_num)
        for w in range(0, NUM_WEEKS_DISPLAY):
            
            # [6, 0, 1, 2, 3, 4, 5]
            for d in range(6, 6 + NUM_DAYS_IN_WEEK):
                upper_left = self.day_starts[(w, d % NUM_DAYS_IN_WEEK)]
                relative_day = d - (NUM_DAYS_IN_WEEK - 1)
                # first arg is (x, y) coord
                # second is the actual number we want as a string
                # current_date = (day_before + relative_day + (w * NUM_DAYS_IN_WEEK)) % days_in_month + 1
                self.dates_to_relative_days[(current_date.year, current_date.month, current_date.day)] = (w, d % NUM_DAYS_IN_WEEK)
                self.dates_to_day_objs[current_date.date()] = Day((w, d % NUM_DAYS_IN_WEEK), 
                                                                current_date, upper_left, PADDING,
                                                                self.day_width)
                draw.text((upper_left[0] + PADDING, upper_left[1] + PADDING), 
                            str(current_date.day), font=font, fill=0)
                current_date = current_date + timedelta(days=1)

        print(self.dates_to_relative_days)

        # add month name at the top
        month_name = cal.month_name[start_month_num]
        draw.text(((self.width // 2) - (len(month_name) // 2), 10), 
                    str(month_name), font=font, fill=0)

        # add day names above columns for the first week
        for d in range(6, 6 + NUM_DAYS_IN_WEEK):
            upper_left = self.day_starts[(0, d % NUM_DAYS_IN_WEEK)]
            relative_day = d - (NUM_DAYS_IN_WEEK - 1)
            day_name = cal.day_name[relative_day]
            draw.text((upper_left[0] + PADDING, upper_left[1] - (PADDING * 2)), 
                    str(day_name), font=font, fill=0)

        return plane

    
    def add_event(self, event_obj: dict):
        # Example: {'summary': 'Elire - Pool', 'allday': False, 
        # 'startDatetime': datetime.datetime(2025, 8, 6, 18, 0, tzinfo=<DstTzInfo 'US/Eastern' EDT-1 day, 20:00:00 DST>), 
        # 'endDatetime': datetime.datetime(2025, 8, 6, 21, 30, tzinfo=<DstTzInfo 'US/Eastern' EDT-1 day, 20:00:00 DST>), 
        # 'updatedDatetime': datetime.datetime(2025, 7, 2, 11, 12, 17, 749000, tzinfo=<DstTzInfo 'US/Eastern' EDT-1 day, 20:00:00 DST>), 
        # 'isUpdated': False, 'isMultiday': False}
        

        event_date_start = event_obj["startDatetime"]

        # if the date is not in the display, ignore it
        if event_date_start.date() not in self.dates_to_day_objs:
            return False 

        # # get the relative day for this event
        event_date_end = event_obj["endDatetime"]
        
        # get the correct day obj
        target_day = self.dates_to_day_objs[event_date_start.date()]

        if not event_obj["isMultiday"]:
            if event_obj["allday"]:
                target_day.add_allday_event(event_obj)
            else:
                target_day.add_event(event_obj)
        else:
            # TODO: deal with all day and multi-day events
            target_day.add_multiday_event(event_obj)
        
        print(target_day)
        print()
        return True

    def update_events(self, img):
        # TODO: combine with render eventually
        # we have the basic skeleton drawn with lines and date numbers
        draw = ImageDraw.Draw(img)

        for target_date, target_day in self.dates_to_day_objs.items():
            
            event_y = target_day.upper_left[1] + (PADDING * 4)
            event_x = target_day.upper_left[0] + PADDING
            # TODO: first, deal with multi-day events

            # next, deal with all day events
            # for event in target_day.all_day_events:
            #     # ImageDraw.rectangle(xy, fill=None, outline=None, width=1)
            #     start = (event_x, event_y)
            #     end = (start[0] + self.day_width - (PADDING * 2), start[1] + (PADDING * 2))
            #     draw.rectangle([start, end], fill = 0, width = 2)
            #     event_y += 30

            # next, deal with regular events
            print(self.day_width)
            for event in target_day.events:
                start = (event_x, event_y)
                end = (start[0] + self.day_width - (PADDING * 2), start[1] + (PADDING * 4))
                # bounding box
                draw.rectangle([start, end], fill = 1, outline = 0, width = 2)
                # text
                text = event["summary"]
                # clip text if needed
                if len(text) > self.day_width / 6:
                    text = text[:(self.day_width // 6) - 5]
                    text += "..."
                start_time = event["startDatetime"]
                end_time = event["endDatetime"]
                time_text = start_time.strftime('%I:%M%p') + " - " + end_time.strftime('%I:%M%p')
                draw.text([start[0] + PADDING, start[1] + PADDING // 2], time_text)#, font=font, fill=0)
                draw.text([start[0] + PADDING, start[1] + (2 * PADDING + (PADDING // 3))], text)#, font=font, fill=0)
                event_y += EVENT_HEIGHT



        


if __name__ == "__main__":
    print("Picture generation testing")
    ph = PictureHelper(960, 480)
    print(ph.get_date_area(0, 0))
    # July 7th
    pic = ph.render(7, 7, 2025)

    # read in the example data 
    with open('../data/events.pickle', 'rb') as f:
        # The protocol version used is detected automatically, so we do not
        # have to specify it.
        events = pickle.load(f)
    # print(events)
    print()
    print("Adding event!")
    for event in events:
        ph.add_event(event)

    print("updating image")
    ph.update_events(pic)
    pic.save("pic.jpg")