#!/usr/bin/python3
import schedule
import time
import os
from twilio.rest import Client
from models.Schedule import Create_Schedule


class Reminder:
    def __init__(self, usr) -> None:
        self.usr = usr
        self.__acct_sid = os.environ["TWILIO_ACCOUNT_SID"]
        self.__auto_token = os.environ["TWILIO_AUTH_TOKEN"]
        self.__from_no = os.environ["TWILIO_WHATSAPP_NO"]
        self.__to_no = os.environ["MY_NUMBER"]
        self.schedule = Create_Schedule(self.usr)
        self.data = self.schedule.View("daily", None)
        self.reminder = None
        self.message = None

    def Get_daily(self) -> None:
        """
            returns messsage displaying current daily task
        """
        return self.message

    def Twilio(self, **kwargs) -> None:
        """
            establish a connection to the Twilio API
        """
        try:

            if kwargs is None:
                text = self.message
            else:
                text = kwargs.get("text")
            client = Client(self.__acct_sid, self.__auto_token)
            client.messages.create(
                        body=text,
                        from_=self.__from_no,
                        to=self.__to_no,
                    )
        except Exception as e:
            print('Failed', e)

    def send_Reminder(self) -> None:
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
