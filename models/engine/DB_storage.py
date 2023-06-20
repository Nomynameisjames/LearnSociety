#!/usr/bin/python3
import sqlalchemy
import os
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from models.baseModel import User, Base, user_id


class DBstorage:
    _engine = None
    _session = None
    """
        The __init__ method used to create a connection to the database
    """
    def __init__(self):
        Mysql_User = os.getenv('MYSQL_USR')
        Mysql_Host = os.getenv('MYSQL_HOST')
        Mysql_Pass = os.getenv('MYSQL_PASS')
        Mysql_Db = None#os.getenv('MYSQL_TEST_DB')
        port = os.getenv('PORT')
        if Mysql_Db is None:
            Mysql_Db = os.getenv('MYSQL_DB')
        self._engine = create_engine('mysql://{}:{}@{}:{}/{}'.
                                      format(Mysql_User,
                                             Mysql_Pass,
                                             Mysql_Host,
                                             port,
                                             Mysql_Db),
                                      pool_recycle=3600,
                                      pool_size=10,
                                      max_overflow=20)
        if os.environ.get("DB_ENV") == 'test':
            Base.metadata.drop_all(self._engine)
    """
       The View method is used to get the user data from the database
       it takes in the user_id object as an argument and returns a dictionary
       of all user items in the database
    """

    def view(self, my_id):
        table = user_id
        my_dict = {}
        tasks = {}
        objs = self._session.query(table).all()

        for task in objs:
            key = task.id
            my_dict[key] = task

        data = my_dict.get(my_id)
        if data and data.schedules != []:
            file = data.schedules
            for items in file:
                tasks[items.id] = {
                        "Date": items.Days,
                        "Course": items.Course,
                        "Topic": items.Topic,
                        "Reminder": items.Reminder,
                        "Target": items.Target,
                        "Average": items.Average,
                        "Created_at": items.Created_at,
                        "Updated_at": items.Updated_at
                    }
        return my_dict, tasks


    def find_user_by(self, **kwargs):
        """finds a user based on the kwargs provided in DB"""

        try:
            value = self._session.query(user_id) \
                                 .filter_by(**kwargs) \
                                 .first()
        except TypeError:
            raise InvalidRequestError("Missing some parameters")

        return value


    """
        access method gets the users data from the database it takes 3 args
        obj, key, arg. arg is the user_id class object, key is the column name
        and obj is the value of the column
    """
    def access(self, obj, key, arg):
        index = {'Email': user_id.Email,
                 'Password': user_id.Password,
                 'User_name': user_id.User_name,
                 'id': user_id.id}

        query = self._session.query(arg)
        data = query.filter(index[key] == obj).first()
        return data

    def new(self, obj):
        """
            add the object to the current database session
        """
        self._session.add(obj)

    def save(self):
        """
            commit all changes of the current database session
        """
        self._session.commit()

    def delete(self, obj=None):
        """
            delete from the current database session obj if not None
        """
        if obj is not None:
            self._session.delete(obj)
        self.save()

    def reload(self):
        """
            reloads data from the database
        """
        Base.metadata.create_all(self._engine)
        sess_factory = sessionmaker(bind=self._engine, expire_on_commit=False)
        Session = scoped_session(sess_factory)
        self._session = Session
    
    def rollback_session(self):
        """
            rollsback a session in the event of an exception
        """
        self._session.rollback()
    

    def close(self):
        """
            call remove() method on the private session attribute
        """
        self._session.remove()
