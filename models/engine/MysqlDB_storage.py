#!/usr/bin/python3
import os
import sqlalchemy
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.pool import QueuePool
from typing import Dict, Union, Tuple
from dotenv import load_dotenv
from models.baseModel import Base, user_id

load_dotenv()


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
        Mysql_Db = None
        port = os.getenv('PORT')
        _database_url = ""
        if Mysql_Db is None:
            Mysql_Db = os.getenv('MYSQL_DB')
            _database_url = (
                    f'mysql://{Mysql_User}:{Mysql_Pass}@{Mysql_Host}:{port}/'
                    f'{Mysql_Db}'
                    )
        pool_size = 10
        max_overflow = 5
        pool_timeout = 30
        pool_recycle = 3600
        self._engine = create_engine(_database_url,
                                     poolclass=QueuePool,
                                     pool_size=pool_size,
                                     max_overflow=max_overflow,
                                     pool_timeout=pool_timeout,
                                     pool_recycle=pool_recycle
                                     )
        if os.getenv("DB_ENV") == 'test':
            Base.metadata.drop_all(self._engine)

    """
       The View method is used to get the user data from the database
       it takes in the users id as an argument and returns a tuple the first
       element in the tuple is a dictionary representataion of the user_id
       object with the users id as the key and the value a user_id object.
       the second element returned in tuple is the users self customised tasks
       queried based on a one to many relationship with the user_id object.
    """

    def view(self, my_id: str)\
            -> Tuple[Dict[str, user_id], Dict[str, Dict[str, str]]]:
        if not isinstance(my_id, str):
            raise TypeError("my_id must be a string")
        table = user_id
        my_dict = {}
        tasks = {}
        objs = []
        if self._session:
            objs = self._session.query(table).all()

        for task in objs:
            if task.ID == my_id:
                key = task.ID
                my_dict[key] = task
        data = my_dict.get(my_id)
        if data and data.schedules != []:
            file = data.schedules
            for items in file:
                tasks[items.ID] = {
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

    """
        access method gets the users data from the database in a more precise
        manner it takes 3 args
        1. mode: which represent the mode to query the user_id obj
        2. key: specific means to access the user_id obj
        3. Obj: the user_id class object which represent an ORM class that maps
           the mysql database table to a python class
        the method returns the user_id object if found else None
    """
    def access(self, mode: str, key: str, obj: user_id)\
            -> Union[None, user_id]:
        index = {'Email': user_id.Email,
                 'Password': user_id.Password,
                 'User_name': user_id.User_name,
                 'id': user_id.ID}
        data = None
        if self._session:
            try:
                data = self._session.query(obj).filter(
                        index[key] == mode).first()
            except Exception as e:
                print(e)
                self.rollback_session()
        return data

    def search(self, key: str, obj: user_id) -> Union[None, list]:
        data = None
        if key and self._session:
            data = self._session.query(obj).filter(
                    obj.User_name.icontains(key) | obj.Email.icontains(key)
                    ).order_by(obj.ID).limit(10).all()
        return data

    def new(self, obj: user_id) -> None:
        """
            add the object to the current database session
        """
        if obj is not None and self._session:
            self._session.add(obj)

    def save(self) -> None:
        """
            commit all changes of the current database session
        """
        if self._session:
            self._session.commit()

    def delete(self, obj=None) -> None:
        """
            delete from the current database session obj if not None
        """
        if obj is not None and self._session:
            self._session.delete(obj)
        self.save()

    def reload(self) -> None:
        """
            reloads data from the database
        """
        Base.metadata.create_all(self._engine)
        sess_factory = sessionmaker(bind=self._engine, expire_on_commit=False)
        Session = scoped_session(sess_factory)
        self._session = Session

    def rollback_session(self) -> None:
        """
            rollsback a session in the event of an exception
        """
        if self._session:
            self._session.rollback()

    def close(self) -> None:
        """
            call remove() method on the private session attribute
        """
        if self._session:
            self._session.remove()
