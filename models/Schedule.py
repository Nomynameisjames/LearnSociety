#!/usr/bin/python3
from sqlalchemy import false
import models
from models.baseModel import User, Base
from datetime import date, datetime
from models.baseModel import user_id

class Create_Schedule(User):
    """ 
        Class Create, updates and delete a new instance of the User class
    """
    # defines datetime attritributes 
    now_T = datetime.now()
    now = datetime(now_T.year, now_T.month, now_T.day, now_T.hour,
                   now_T.minute, 0)
    # init method stores the data queried from the database
    def __init__(self, my_id):
        self.my_id = my_id
        self.__data = models.storage.view(self.my_id)
        self.user = None

    """
        class method creates a customised schedule for the user, using the
        User class, and saves the data to the database by calling the Save
        method
    """
    def Create(self, **kwargs):
        day = kwargs.get('Day')
        my_course = kwargs.get('Course')
        my_topic = kwargs.get('Topic')
        reminder = kwargs.get('Reminder')
        my_day = datetime.strptime(day, "%Y-%m-%d").date()
        my_reminder = datetime.strptime(reminder, "%H:%M:%S").time()
        if self.my_id is None:
            return f"user not found"
        else:
            self.user = User(
                                Days = my_day,
                                user_ID = self.my_id,
                                Course = my_course,
                                Topic = my_topic,
                                Reminder = my_reminder,
                                Target = False,
                                Average = None,
                                Created_at = self.now,
                                Updated_at = None
                            )

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
    def Delete(self, my_id, deldata=None):
        """
            Deletes all users self customised schedules and modifies data
            queried from the database by userID
        """
        deldata = models.storage.view(my_id)[0].get(str(my_id))
        deldata = deldata.schedules.all()
        if deldata == []:
            return True
        if deldata:
            for data in deldata:
                models.storage.delete(data)
                models.storage.save()
            models.storage.close()
            return True
        else:
            return False

    def View(self, my_id: str, choice: str=None, table: str=None):
        """
            class method queries the database and returns a dictionary value
            based on the specified query method
        """
        new = models.storage.access(my_id, 'id', user_id)
        new_dict = {}
        query_methods = {
            None: new.schedules.all,
            "Python": new.auto_schedules.all,
            "Javascript": new.JScourse.all,
            "React": new.Reactcourse.all,
            "C": new.C_course.all,
        }
        tasks = query_methods.get(table, lambda: None)()
    
        if not tasks:
            return new_dict
        else:

            short_date = self.now.strftime("%Y-%m-%d")

            for task in tasks:
                new_dict[task.id] = {
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
            new_dict_2 = {k:v for k, v in new_dict.items()if v["Date"] > short_date}
        elif str(choice).lower() == "daily":
            new_dict_2 = {k: v for k, v in new_dict.items() if v["Date"] == short_date}
        elif str(choice).lower() == "missed":
            new_dict_2 = {k: v for k, v in new_dict.items() if v["Date"] < short_date and not v['Target']}
        else:
            raise ValueError(f"Invalid choice {choice}")
        models.storage.close()
        return new_dict_2

        
    def Target(self, my_id: str, course: str) -> tuple:
        """
            method calculates the average target of the user based on the
            course specified and returns a tuple of the average target and
            the data queried from the database
        """
        data = self.__data[0].get(my_id)
        if not data:
            return (0, {})
        file = {
                "Python" : data.auto_schedules.all(),
                "Javascript" : data.JScourse.all(),
                "React" : data.Reactcourse.all(),
                "C" : data.C_course.all()
            }
        if not file.get(course):
            return (0, file)
        else:
            python_Target = [x.Target for x in file.get(course)]
            python_Target = [int(b) for b in python_Target]
            python_mean_Target = sum(python_Target) / len(python_Target)
            python_mean_Target = round(python_mean_Target, 2)
            return (python_mean_Target, file)
    
    def DeleteAll(self, my_id: str, course: list) -> bool:
        """
            method deletes all automated schedules created by the user
        """
        course_file = []
        for idx, file  in enumerate(course):
            if idx > 0:
                break
            course_file.append(self.Target(my_id, file)[1])

        course_file = course_file[0]
        if all(not bool(val) for val in course_file.values()):
            return True
        status = False
        while any(course_file.values()):
            for _, value in course_file.items():
                if value == []:
                    continue
                for val in value:
                    models.storage.delete(val)
                    models.storage.save()
                    value.remove(val)
                    status = True
            models.storage.close()
        return status
