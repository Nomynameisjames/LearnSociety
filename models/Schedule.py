#!/usr/bin/python3
from datetime import datetime
from typing import Union, Tuple
from .baseModel import User, user_id
from typing import Union, Tuple
import models


class Create_Schedule(User):
    """
        Class Create, updates and delete a new instance of the User class
    """
    now_T = datetime.now()
    now = datetime(now_T.year, now_T.month, now_T.day, now_T.hour,
                   now_T.minute, 0)
    # init method stores the data queried from the database

    def __init__(self, my_id: str) -> None:
        self.my_id = my_id
        self.__data = models.storage.access(self.my_id, 'id', user_id)
        self.user = None
        self.file = {}
        if self.__data:
            self.file = {
                    None: self.__data.schedules.all(),
                    "Python": self.__data.auto_schedules.all(),
                    "Javascript": self.__data.JScourse.all(),
                    "React": self.__data.Reactcourse.all(),
                    "C": self.__data.C_course.all()
                }

    """
        class method creates a customised schedule for the user, using the
        User class, and saves the data to the database by calling the Save
        method
    """
    @property
    def coursefile(self):
        return self.file

    def Create(self, **kwargs) -> None:
        day = kwargs.get('Day')
        reminder = kwargs.get('Reminder')
        set_day, set_reminder = None, None
        if day and reminder:
            set_day = datetime.strptime(day, "%Y-%m-%d").date()
            set_reminder = datetime.strptime(reminder, "%H:%M:%S").time()
        if self.my_id is None:
            return
        else:
            self.user = User(
                    Days=set_day,
                    user_ID=self.my_id,
                    Course=kwargs.get('Course'),
                    Topic=kwargs.get('Topic'),
                    Reminder=set_reminder,
                    Target=False,
                    Average=None,
                    Created_at=self.now,
                    Updated_at=None)

    # saves newly created instance of the User class and commits to database
    def Save(self) -> bool:
        """
            class method saves the newly created data from class instance to
            the database
        """
        models.storage.new(self.user)
        models.storage.save()
        models.storage.close()
        return True

    # deletes an instance of the User class and removes data from database
    def Delete(self) -> Union[bool, None]:
        """
            Deletes all users self customised schedules and modifies data
            queried from the database by userID
        """
        if self.__data is None:
            return
        delete_files = self.__data.schedules.all()
        if delete_files == []:
            return True
        if delete_files:
            for data in delete_files:
                models.storage.delete(data)
                models.storage.save()
            models.storage.close()
            return True
        else:
            return False

    def View(self, choice=None, table=None) -> dict:
        """
            class method queries the database and returns a dictionary value
            based on the specified query method
        """
        new_dict = {}
        if self.__data is None:
            return new_dict
        tasks = self.file.get(table)
        if not tasks:
            return new_dict
        else:
            short_date = self.now.strftime("%Y-%m-%d")
            for task in tasks:
                new_dict[task.ID] = {
                    "Date": task.Days,
                    "Course": task.Course,
                    "Topic": task.Topic,
                    "Target": task.Target,
                    "Average": task.Average,
                    "Reminder": task.Reminder,
                    "Created": task.Created_at,
                    "Updated": task.Updated_at,
                }
        if choice is None:
            return new_dict
        elif str(choice).lower() == "upcoming":
            new_dict_2 = {k: v for k, v in new_dict.items()
                          if v["Date"] > short_date}
        elif str(choice).lower() == "daily":
            new_dict_2 = {k: v for k, v in new_dict.items()
                          if v["Date"] == short_date}
        elif str(choice).lower() == "missed":
            new_dict_2 = {k: v for k, v in new_dict.items()
                          if v["Date"] < short_date and not v['Target']}
        else:
            raise ValueError(f"Invalid choice {choice}")
        models.storage.close()
        return new_dict_2

    def Target(self, course: str) -> Union[float, None]:
        """
            method calculates the average target of the user based on the
            course specified and returns a tuple of the average target and
            the data queried from the database
        """
        data = []
        if self.__data:
            data = self.file.get(course)
        if data:
            Target = [x.Target for x in data]
            course_Target = [int(b) for b in Target]
            course_mean_Target = sum(course_Target) / len(course_Target)
            average_Target = round(course_mean_Target, 2)
            return average_Target
        else:
            return

    def DeleteAll(self) -> bool:
        """
            method deletes all automated schedules created by the user
        """
        if all(not bool(val) for val in self.file.values()):
            return True
        status = False
        while any(self.file.values()):
            for _, value in self.file.items():
                if value == []:
                    continue
                for val in value:
                    models.storage.delete(val)
                    models.storage.save()
                    value.remove(val)
                    status = True
            models.storage.close()
        return status
