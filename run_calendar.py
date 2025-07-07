from gcal.gcal import GcalHelper
from display.picture import PictureHelper
import datetime as dt
import logging
import sys
import os
import json
from pytz import timezone
import pickle

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

def main():
    logging.basicConfig(filename="logfile.log", format='%(asctime)s %(levelname)s - %(message)s', filemode='a')
    logger = logging.getLogger('maginkcal')
    logger.addHandler(logging.StreamHandler(sys.stdout))  # print logger to stdout
    logger.setLevel(logging.INFO)
    logger.info("Starting daily calendar update")

    # load settings
    if os.path.exists("calendar_settings.json"):
      with open("calendar_settings.json", "r") as file:
          settings = json.load(file)
          cal_id = settings["calendarId"]
    else:
        print("Reading from primary calendar")


    # just testing to start with
    gcal = GcalHelper(calendar_id=cal_id)
    gcal.list_calendars()

    displayTZ = timezone("US/Eastern")
    thresholdHours = 12
    # 0 = Monday, 6 = Sunday
    weekStartDay = 0
    currDatetime = dt.datetime.now()
    logger.info("Time synchronised to {}".format(currDatetime))
    currDate = currDatetime.date()
    calStartDate = currDate - dt.timedelta(days=((currDate.weekday() + (7 - weekStartDay)) % 7))
    calEndDate = calStartDate + dt.timedelta(days=(5 * 7 - 1))
    calStartDatetime = displayTZ.localize(dt.datetime.combine(calStartDate, dt.datetime.min.time()))
    calEndDatetime = displayTZ.localize(dt.datetime.combine(calEndDate, dt.datetime.max.time()))

    # Using Google Calendar to retrieve all events within start and end date (inclusive)
    start = dt.datetime.now()
    eventList = gcal.retrieve_events([cal_id], calStartDatetime, calEndDatetime, displayTZ, thresholdHours)
    # print(type(eventList))
    # pickle and save the event list (mostly for debugging)
    for event in eventList:
        logger.info(f"Event: {event}")
        # print(type(event))
        # print(type(event["startDatetime"]))

    with open('data/events.pickle', 'wb') as f:
        # Pickle the 'data' dictionary using the highest protocol available.
        pickle.dump(eventList, f, pickle.HIGHEST_PROTOCOL)
    print("pickled!")
        
    logger.info("Calendar events retrieved in " + str(dt.datetime.now() - start))





if __name__ == "__main__":
    main()