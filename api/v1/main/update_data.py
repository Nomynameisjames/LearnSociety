#!/usr/bin/env python3
from models import storage, redis_storage
from models.Schedule import Create_Schedule as cs
from models.baseModel import user_id
from models.RequestModule import Notifications
from models.Update_Profile import update_redis_profile
from werkzeug.security import check_password_hash, generate_password_hash
from flask import request
from datetime import datetime, timedelta
from typing import Union, Dict
from uuid import uuid4
from string import ascii_uppercase
import random

def generate_unique_code(length):
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
    token = user.generate_confirmation_code()
    code = token[0]
    mydic = {
        "message": f"""Please enter the following code on the confirmation page
                     to reset your email address:<b>{code}</b>""",
         "header": "Email Address Reset",
         "subject": "Email Confirmation",
     }
    return mydic

def create_community(ID, **kwargs):
    """
        function that creates a community
    """
    admin_user = storage.access(ID, 'id', user_id)
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
    ID = uuid4()
    Community = {
            str(ID): {
                "name": kwargs.get('name'),
                "users": [admin_user.User_name],
                "chat": [{
                          "text": "",
                          "sender": "",
                          "date": ""
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

def update_profile(ID: str, item: str, value: Union[str, int, bool]):
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
            "password":"Password",
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
    def __init__(self, current_user):
        self.ID = current_user.id
        self.data = request.get_json()
        self.usr = storage.access(self.ID, 'id', user_id)
        self.course_list = cs(self.ID)
        self.uploader = update_redis_profile(self.ID)


    def check_credentials(self, password: str):
        """
            class method is called to check the user password against the
            password in the database
        """
        if self.usr and check_password_hash(self.usr.Password, str(password)):
            return True
        else:
            return False

    def update_username(self):
        """
            class method is called to update the user username by first checking
            if the password sent in the request payload is correct
        """
        obj = self.data.get('Key')
        value = self.data.get('Value')
        if obj is not None:
            if self.check_credentials(obj):
                profile = update_profile(self.ID, 'username', value)
                if profile:
                    return True
                else:
                    return False

        profile = update_profile(self.ID, 'username', self.data.get('username'))
        if profile:
            return True
        else:
            return False

    def update_email(self):
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
            else:
                return False

    def update_course_tempo(self):
        """
            class method updates the users  auto courses tempo by adjusting
            daily schedule by the tempo sent in the request payload
        """
        tempo = int(self.data.get('tempo'))
        delta = 0
        course = self.data.get('course')
        course_file = self.course_list.Target(self.ID, course)[1]
        if course_file:
            now = datetime.utcnow().date()
            course_file = course_file.get(course)
            for item in course_file:
                cur_date = datetime.strptime(item.Days, '%Y-%m-%d').date()
                if cur_date >= now:
                    delta = delta + tempo
                    cur_date = cur_date + timedelta(days=delta)
                    item.Days = cur_date.strftime('%Y-%m-%d')
            storage.save()
            storage.close()
            return True
        else:
            return False

    def update_contact(self):
        """
            class method updates the users contact information
        """
        profile = update_profile(self.ID, 'phone_number', self.data.get('phone_number'))
        if profile:
            return True
        else:
            return False

    def update_password(self):
        """
            class method updates the users password by first checking if the
            old password sent in the request payload is correct
        """
        if self.check_credentials(self.data.get('old_password')):
            if self.data.get('new_password') == self.data.get('confirm_password'):
                value = generate_password_hash(self.data.get('new_password'))
                profile = update_profile(self.ID, 'password', str(value))
                if profile:
                    return True
                else:
                    return False
            else:
                return False
        else:
            return False

    def send_user_notification(self):
        """
            class method sends the user a notification
        """
        if self.usr:
            Notify = Notifications()
            email_content = compose_message(self.usr)
            send_notification = Notify.send_Grid(self.usr, **email_content)
            if send_notification:
                return f"confirmaion code sent to {self.usr.Email}"
            else:
                return False
        else:
            return False

    def verify_confirmation_code(self):
        """
            class method verifies the confirmation code sent in the request
            payload
        """
        code = self.data.get('code')
        if self.usr and self.usr.verify_confirmation_code(code):
            return f"code verified"
        else:
            return False

    def update_save_history(self):
        """
            class method updates the users save history
        """
        opt = self.data.get('isChecked')
        profile = update_profile(self.ID, 'save_history', opt)
        if profile:
            return f"save history updated"
        else:
            return False

    def delete_chat_history(self):
        """
            class method deletes the users chat history
        """
        if self.ID != self.data.get('id'):
            return False
        else:
            self.uploader.clear_chatbot_history()
            return f"chat history deleted"

    def delete_auto_course(self):
        """
            class method deletes the users auto course
        """
        course = self.data.get('course')
        course_file = self.course_list.Target(self.ID, course)[1]
        file = None
        course_file = course_file.get(course)

        if course_file:
            for item in course_file:
                if item.user_ID == self.ID:
                    file = item
                storage.delete(file)
                storage.save()
            storage.close()
            return f"deleted {course} tutorials successfully"
        else:
            return False

    def delete_account(self):
        """
            class method deletes the users account
        """
        confirmDelete = self.data.get('confirmDelete')
        Auto_courses = ["Python", "C", "React", "Javascript"]
        user = storage.view(self.ID)[0].get(self.ID)
        Delete_auto_courses = self.course_list.DeleteAll(self.ID, Auto_courses)
        Delete_custom_courses = self.course_list.Delete(self.ID, None)
        if Delete_auto_courses and Delete_custom_courses:
            if user.id == self.ID and confirmDelete:
                storage.delete(user)
                storage.save()
            storage.close()
            return f"account deleted goodbye"
        else:
            return False

