#!/usr/bin/python3
import time
import os
from models.Schedule import Create_Schedule
from datetime import datetime
from twilio.rest import Client
import schedule

current_date_time = datetime.now()
now = current_date_time.strftime("%Y-%m-%d")
class Reminder:
    def __init__(self, usr):
        self.usr = usr
        self.__acct_sid = os.environ["TWILIO_ACCOUNT_SID"]
        self.__auto_token = os.environ["TWILIO_AUTH_TOKEN"]
        self.__from_no = os.environ["TWILIO_WHATSAPP_NO"]
        self.__to_no = os.environ["MY_NUMBER"]
        self.schedule = Create_Schedule(self.usr)
        self.data = self.schedule.View(self.usr, "daily")
        self.reminder = None
        self.message = None


    def Get_daily(self):
        """
            returns messsage displaying current daily task 
        """
        return self.message
        

    def Twilio(self, **kwargs):
        """
            establish a connection to the Twilio API 
        """
        try:

            if kwargs is None:
                text = self.message
            else:
                text = kwargs.get("text")
            client = Client(self.__acct_sid, self.__auto_token)
            session = client.messages.create(
                        body=text,
                        from_=self.__from_no,
                        to=self.__to_no,
                        )
            return session
        except Exception as e:
            print('Failed', e)
            return e
    def send_Reminder(self):
        """
            having established a connection funtion sends a reminder using the
            twilio api to designated number.
        """
        try:
            if self.reminder:
                    clock = str(self.reminder)
                    schedule.every().day.at(clock).do(self.Twilio)
                    while True:
                        """ 
                            loops every 10 seconds to check if there are any
                            active reminder
                        """
                        schedule.run_pending()
                        time.sleep(10)
            else:
                    print(">>> no reminder set")
            print("**** Done! ****")
        except Exception as e:
            print("Failed to establish connection", e)
