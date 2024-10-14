#!/usr/bin/python3
from datetime import datetime, timedelta
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from flask_login import UserMixin
from typing import Any, Tuple
import random
import time
import string
import jwt
import models

"""
    This module contains the base model for the mysql database tables
    and the classes that map out the tables in the database
"""
Base = declarative_base()


class Auto_courses:
    Days = Column(DateTime)
    Course = Column(String(50))
    Topic = Column(String(50))
    Reminder = Column(DateTime)
    Target = Column(Boolean)
    Created_at = Column(DateTime, default=datetime.utcnow)
    Updated_at = Column(DateTime)
    Average = Column(Integer)

    def __str__(self):
        """
            returns a string representation of the class
        """
        return f"Date: {self.Days} Course: {self.Course} Topic: {self.Topic}\
                Average: {self.Average} Reminder: {self.Reminder}\
                Created: {self.Created_at}"


class User(Base, Auto_courses):
    """
        class maps out a table in the mysql database that stores a users self
        customised task creating an object representation
    """
    __tablename__ = 'January'
    ID = Column(Integer, primary_key=True)
    user_ID = Column(Integer, ForeignKey('user_info.ID'))


class AutoSchedule(Base, Auto_courses):
    """
        class maps out a table in the mysql database that stores a users
        Python course info creating an object representation
    """
    __tablename__ = 'PythonDB'
    ID = Column(Integer, primary_key=True)
    user_ID = Column(Integer, ForeignKey('user_info.ID'))


class JSCourse(Base, Auto_courses):
    """
        class maps out a table in the mysql database that stores a users
        Javascript course info creating an object representation
    """
    __tablename__ = 'JavascriptDB'
    ID = Column(Integer, primary_key=True)
    user_ID = Column(Integer, ForeignKey('user_info.ID'))


class ReactCourse(Base, Auto_courses):
    """
        class maps out a table in the mysql database that stores a users
        React course info creating an object representation
    """
    __tablename__ = 'ReactDB'
    ID = Column(Integer, primary_key=True)
    user_ID = Column(Integer, ForeignKey('user_info.ID'))


class C_Course(Base, Auto_courses):
    """
        class maps out a table in the mysql database that stores a users
        C course info creating an object representation
    """
    __tablename__ = 'C-DB'
    ID = Column(Integer, primary_key=True)
    user_ID = Column(Integer, ForeignKey('user_info.ID'))


class user_id(Base, UserMixin):
    """
        creates a class representation of the user info table in the mysql
        database
    """
    __tablename__ = 'user_info'
    ID = Column(String(255), primary_key=True)
    User_name = Column(String(100))
    Email = Column(String(100))
    Password = Column(String(300))
    Phone_number = Column(String(100))
    Created_at = Column(DateTime, default=datetime.now)
    Updated_at = Column(DateTime)
    save_history = Column(Boolean)
    Rooms = Column(Integer, default=0)
    schedules = relationship('User', backref='January', lazy='dynamic')
    auto_schedules = relationship('AutoSchedule', backref='PythonDB',
                                  lazy='dynamic')
    JScourse = relationship('JSCourse', backref='JSCourse', lazy='dynamic')
    Reactcourse = relationship('ReactCourse', backref='ReactDB',
                               lazy='dynamic')
    C_course = relationship('C_Course', backref='C-DB', lazy='dynamic')

    def __str__(self) -> str:
        """
            returns string representation of class objects
        """
        return (f"id : {self.ID}, username:"
                f"{self.User_name} email: {self.Email}")

    """
        Flask-Login integration checks if a user is currently logged in
        to a session
    """
    def is_active(self) -> bool:
        return True

    def get_id(self) -> str:
        return str(self.ID)

    def get_reset_token(self) -> str:
        """
            generates a jwt token for a user to reset their password
        """
        from web_flask.app import app
        user = models.storage.access(str(self.ID), 'id', user_id)
        if not user:
            raise Exception('User not found')
        token = token_payload = {'user_id': str(self.ID),
                                 'exp': datetime.utcnow()
                                 + timedelta(minutes=2)}
        token = jwt.encode(token_payload, app.config['SECRET_KEY'])
        return token.encode('utf-8').decode()

    @staticmethod
    def verify_reset_token(token: str) -> Any:
        """
            verifies the validity of a jwt token for a user to reset their
            password if true returns an instance of the user
        """
        from web_flask.app import app
        try:
            token_payload = jwt.decode(token, app.config['SECRET_KEY'],
                                       algorithms=["HS256"])
            my_id = token_payload['user_id']
        except jwt.ExpiredSignatureError:
            return None
        except (jwt.InvalidTokenError, KeyError):
            return None
        user = models.storage.access(my_id, 'id', user_id)
        return user

    def generate_confirmation_code(self) -> Tuple[str, float]:
        """
            generates a confirmation code for a user to confirm their email
            saves the code to a json file and returns the code and its
            expiration time
        """
        code = ''.join(random.choices(string.ascii_letters +
                                      string.digits, k=8))
        now = time.time()
        key = f'{self.ID}:code'
        expiration_time = now + 600
        data = {'code': code, 'expiration_time': expiration_time}
        models.redis_storage.set_dict(key, data, 700)
        return (code, expiration_time)

    def verify_confirmation_code(self, code: str) -> bool:
        """
            verifies the validity of a confirmation code for a user to confirm
            their email if true returns true
        """
        key = f'{self.ID}:code'
        confirmation_code = models.redis_storage.get_dict(key, 'code')
        expiration_time = models.redis_storage.get_dict(key, 'expiration_time')
        timestamp = float(time.time())
        try:
            expiration_time = float(expiration_time)
            if confirmation_code == code and timestamp - expiration_time < 600:
                models.redis_storage.delete(key)
                return True
        except (ValueError, TypeError):
            pass
        return False

    def active_rooms(self):
        """
            returns the number of active rooms a user has
        """
        community = models.redis_storage.get_list_dict('community')
        if community:
            for items in community:
                for _, value in items.items():
                    if value['admin'] == self.User_name and self.Rooms:
                        return True
        else:
            return False
