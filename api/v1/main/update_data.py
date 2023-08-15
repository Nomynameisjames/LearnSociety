#!/usr/bin/env python3
from werkzeug.security import check_password_hash, generate_password_hash
from flask import request
from flask_login import current_user
from datetime import datetime, timedelta
from typing import Union, Dict
from uuid import uuid4
from string import ascii_uppercase
from models import storage, redis_storage
from models.Schedule import Create_Schedule as cs
from models.baseModel import user_id
from models.RequestModule import Notifications
from models.Update_Profile import update_redis_profile
import random


def generate_unique_code(length: int) -> str:
    """
        generates a unique code for community chat rooms
    """
    community = redis_storage.get_list_dict('community')
    rooms = []
    if community:
        for item in community:
            for _, value in item.items():
                rooms.append(value["code"])
    while True:
        code = ""
        for _ in range(length):
            code += random.choice(ascii_uppercase)
        if code not in rooms:
            break
    return code


def compose_message(user: user_id) -> Dict[str, str]:
    """
        generate a confirmation token as well as compose a message to be sent
        to the users email address
    """
    token = user.generate_confirmation_code()
    code = token[0]
    mydic = {
        "message": f"""Please enter the following code on the confirmation page
                     to reset your email address:<b>{code}</b>""",
        "header": "Email Address Reset",
        "subject": "Email Confirmation"
        }
    return mydic


def create_community(ID: str, **kwargs) -> bool:
    """
        function that creates a new community
    """
    admin_user = storage.access(ID, 'id', user_id)
    if admin_user is None:
        return False
    if not admin_user.active_rooms():
        admin_user.Rooms = 0
        storage.save()
    Check = redis_storage.get_list_dict('community')
    if admin_user.Rooms >= 1:
        return False
    if Check:
        for item in Check:
            for _, value in item.items():
                if value["name"] == kwargs.get('name'):
                    return False
    community_id = uuid4()
    Community = {
            str(community_id): {
                "name": kwargs.get('name'),
                "users": [admin_user.User_name],
                "group_picture": kwargs.get('group_picture'),
                "chat": [{
                          "text": "",
                          "name": "",
                          "time": ""
                          }],
                "admin": kwargs.get('admin'),
                "code": generate_unique_code(6),
                "date": kwargs.get('date'),
                "description": kwargs.get('description')
                }
            }
    admin_user.Rooms = 1
    storage.save()
    redis_storage.set_list_dict('community', [Community])
    return True


def update_profile(ID: str, item: str, value: Union[str, int, bool])\
        -> Union[bool, None]:
    """
        function is called to update the user profile information
        based on the item and value passed in the function
        Args:
            ID: user id
            item: item to be updated
            value: value to be updated
        Return:
            True if the update is successful
    """
    user = storage.access(ID, 'id', user_id)
    if user is None:
        return False
    my_dict = {
            "email": "Email",
            "password": "Password",
            "username": "User_name",
            "phone_number": "Phone_number",
            "save_history": "save_history"
            }
    if item in my_dict:
        Property: str = my_dict[item]
        setattr(user, Property, value)
        user.Updated_at = datetime.now().strftime("%Y-%m-%d")
        storage.save()
        storage.close()
        return True


class Settings:
    """
        class is called to update the user profile information
        via the api endpoint /api/v1/settings does so by sending a request
        and calling the appropriate function based on the request
    """
    def __init__(self, current_user: current_user) -> None:
        self.ID = current_user.ID
        self.data = request.get_json()
        self.usr = storage.access(self.ID, 'id', user_id)
        self.course_list = cs(self.ID)
        self.uploader = update_redis_profile(self.ID)

    def check_credentials(self, password: str) -> bool:
        """
            class method is called to check the user password against the
            password in the database
        """
        if self.usr and check_password_hash(self.usr.Password, str(password)):
            return True
        return False

    def update_username(self) -> bool:
        """
            class method is called to update the user username by first
            checking if the password sent in the request payload is correct
        """
        obj = self.data.get('Key')
        value = self.data.get('Value')
        if obj is not None:
            if self.check_credentials(obj):
                profile = update_profile(self.ID, 'username', value)
                if profile:
                    return True
                return False

        profile = update_profile(self.ID, 'username',
                                 self.data.get('username'))
        if profile:
            return True
        return False

    def update_email(self) -> Union[bool, None]:
        """
            class method updates the user email by first checking if the
            password sent in the request payload is correct
        """
        key = self.data.get('passkey')
        value = self.data.get('email')
        if self.usr and self.check_credentials(key):
            profile = update_profile(self.ID, "email", str(value))
            if profile:
                return True
        return False

    def update_status(self) -> Union[str, None]:
        """
            class method updates the user status by first checking if the
            password sent in the request payload is correct
        """
        value = self.data.get('status')
        if self.usr:
            self.uploader.update_status(value)
            return f"status Update successful"

    def update_course_tempo(self) -> Union[bool, None]:
        """
            class method updates the users  auto courses tempo by adjusting
            daily schedule by the tempo sent in the request payload
        """
        tempo = int(self.data.get('tempo'))
        delta = 0
        course = self.data.get('course')
        course_file = self.course_list.Target(course)
        if course_file and isinstance(course_file, dict):
            now = datetime.utcnow().date()
            data = course_file.get(course)
            if not data:
                return
            for item in data:
                cur_date = datetime.strptime(item.Days, '%Y-%m-%d').date()
                if cur_date >= now:
                    delta = delta + tempo
                    cur_date = cur_date + timedelta(days=delta)
                    item.Days = cur_date.strftime('%Y-%m-%d')
            storage.save()
            storage.close()
            return True
        return False

    def update_contact(self) -> Union[bool, None]:
        """
            class method updates the users contact information
        """
        profile = update_profile(self.ID, 'phone_number',
                                 self.data.get('phone_number'))
        if profile:
            return True
        return False

    def update_password(self) -> Union[bool, None]:
        """
            class method updates the users password by first checking if the
            old password sent in the request payload is correct
        """
        if self.check_credentials(self.data.get('old_password')):
            if self.data.get('new_password') ==\
                    self.data.get('confirm_password'):
                value = generate_password_hash(self.data.get('new_password'))
                profile = update_profile(self.ID, 'password', str(value))
                if profile:
                    return True
        return False

    def send_user_notification(self) -> Union[str, bool]:
        """
            class method sends the user a notification
        """
        if self.usr:
            Notify = Notifications()
            email_content = compose_message(self.usr)
            send_notification = Notify.send_Grid(self.usr, **email_content)
            if send_notification:
                return f"confirmaion code sent to {self.usr.Email}"
        return False

    def verify_confirmation_code(self) -> Union[str, bool]:
        """
            class method verifies the confirmation code sent in the request
            payload
        """
        code = self.data.get('code')
        if self.usr and self.usr.verify_confirmation_code(code):
            return f"code verified"
        return False

    def update_save_history(self) -> Union[str, bool]:
        """
            class method updates the users save history
        """
        opt = self.data.get('isChecked')
        profile = update_profile(self.ID, 'save_history', opt)
        if profile:
            return f"save history updated"
        return False

    def delete_chat_history(self) -> Union[str, bool]:
        """
            class method deletes the users chat history with the OpenAI chatbot
        """
        if self.ID != self.data.get('id'):
            return False
        self.uploader.clear_chatbot_history()
        return f"chat history deleted"

    def delete_auto_course(self) -> Union[str, bool]:
        """
            class method deletes the users auto course
        """
        course = self.data.get('course')
        course_file = self.course_list.Target(course)
        file, data = None, None
        if course_file and isinstance(course_file, dict):
            data = course_file.get(course)
        if data:
            for item in data:
                if item.user_ID == self.ID:
                    file = item
                storage.delete(file)
                storage.save()
            storage.close()
            return f"deleted {course} tutorials successfully"
        return False

    def delete_account(self) -> Union[str, bool]:
        """
            class method deletes the users account
        """
        confirmDelete = self.data.get('confirmDelete')
        user = storage.access(self.ID, 'id', user_id)
        Delete_auto_courses = self.course_list.DeleteAll()
        Delete_custom_courses = self.course_list.Delete()
        delete_redis_data = self.uploader.delete_user_profile()
        if Delete_auto_courses and Delete_custom_courses and delete_redis_data\
                and isinstance(user, user_id):
            if user.ID == self.ID and confirmDelete:
                storage.delete(user)
                storage.save()
            storage.close()
            return f"account deleted goodbye"
        return False
