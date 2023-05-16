#!/usr/bin/python3

from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, SubmitField, BooleanField
from wtforms.validators import (Email, DataRequired, Length, EqualTo,
                                ValidationError, Optional)
import models
from models.RequestModule import Notifications
from models.baseModel import user_id
from flask_babel import lazy_gettext as _l
import re

class RegisterForm(FlaskForm):
    """
        Register form class
    """
    username = StringField(_l("Username"), validators=[DataRequired(),
                                        Length(min=2, max=20)])

    email = StringField(_l("Email"), validators=[DataRequired(), Email()])

    password = PasswordField(_l("Password"), validators=[DataRequired(),
                                                     Length(min=8)])

    confirm_password = PasswordField(_l("Confirm password"),
                            validators= [DataRequired(), EqualTo('password')])

    submit = SubmitField(_l('Sign up'))

    def validate_username(self, username):
        data = models.storage.access(username.data, 'User_name', user_id)
        if data:
            raise ValidationError(_l('Username already taken'))

    def validate_email(self, email):
        data = models.storage.access(email.data, 'Email', user_id)
        if data:
            raise ValidationError(_l('Email already taken'))
        if email.data == '' and len(email.data) < 4:
            raise ValidationError(_l('Email must be at least 4 characters'))
    
    def validate_password(self, password):
        if len(password.data) < 8:
            raise ValidationError(_l('Password must be at least 8 characters'))
        if not any(char.isdigit() for char in password.data):
            raise ValidationError(_l('Password must contain at least 1 number'))



class LoginForm(FlaskForm):
    """
        Login form class
    """
    email = StringField(_l("Email"), validators=[DataRequired(), Email()])
    password = PasswordField(_l("Password"), validators=[DataRequired()])
    remember = BooleanField(_l("Remember Me"))
    submit = SubmitField(_l('Login'))


class RequestResetForm(FlaskForm):
    """
        Request reset form class
    """
    email = StringField(_l('Email'),
                        validators=[DataRequired(), Email()])
    submit = SubmitField(_l('Request Password Reset'))

    def validate_email(self, email):
        user = models.storage.access(email.data, 'Email', user_id)
        #email_checker = Notifications()
        #is_valid = email_checker.is_valid(email.data)
        if user is None:
            raise ValidationError(_l('''There is no account with that email.
                                  You must register first.'''))
        #if not is_valid:
        #    raise ValidationError(_l('Invalid email'))

class ResetPasswordForm(FlaskForm):
    """
        Reset password form class
    """
    password = PasswordField(_l('Password'), validators=[DataRequired()])
    confirm_password = PasswordField(_l('Confirm Password'),
                                     validators=[DataRequired(),
                                                 EqualTo('password')])
    submit = SubmitField(_l('Reset Password'))
    def validate_password(self, password):
        if len(password.data) < 8:
            raise ValidationError(_l('Password must be at least 8 characters'))
        if not any(char.isdigit() for char in password.data):
            raise ValidationError(_l('Password must contain at least 1 number'))

class SearchBar(FlaskForm):
    """
        search bar form class, handles all search input fields
    """
    search = StringField(_l("Search"), validators=[DataRequired()])
    password = PasswordField(_l('Password'), validators=[Optional()])
    old_password = PasswordField(_l('Old Password'), validators=[Optional()])
    new_password = PasswordField(_l('New Password'), validators=[Optional()])
    confirm_password = PasswordField(_l('Confirm Password'), validators=[Optional()])
    submit = SubmitField(_l('Search'))

    def validate_search(self, search):
        if not re.match(r"^[a-zA-Z0-9_.,'\[\]\(\)\-\s]+$", search.data):
            raise ValidationError(_l('Invalid input parameters'))
