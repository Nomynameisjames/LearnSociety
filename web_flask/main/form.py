#!/usr/bin/python3
from flask_wtf import FlaskForm
from wtforms import (PasswordField, StringField, SubmitField,
                     BooleanField, FileField)
from wtforms.validators import (Email, DataRequired, Length, EqualTo,
                                ValidationError, Optional)
from flask_wtf.file import FileAllowed, FileRequired
from flask_babel import lazy_gettext as _l
from models.baseModel import user_id
import models
import re


class RegisterForm(FlaskForm):
    """
        Register form class to enable user registeration
    """
    username = StringField(_l("Username"), validators=[DataRequired(),
                                                       Length(min=2, max=20)])

    email = StringField(_l("Email"), validators=[DataRequired(), Email()])

    password = PasswordField(_l("Password"), validators=[DataRequired(),
                                                         Length(min=8)])

    confirm_password = PasswordField(_l("Confirm password"),
                                     validators=[
                                         DataRequired(), EqualTo('password')
                                         ])

    submit = SubmitField(_l('Sign up'))

    def validate_username(self, username: FlaskForm) -> None:
        data = models.storage.access(username.data, 'User_name', user_id)
        if data:
            raise ValidationError(_l('Username already taken'))

    def validate_email(self, email: FlaskForm) -> None:
        data = models.storage.access(email.data, 'Email', user_id)
        if data:
            raise ValidationError(_l('Email already taken'))
        if email.data == '' and len(email.data) < 4:
            raise ValidationError(_l('Email must be at least 4 characters'))

    def validate_password(self, password: FlaskForm) -> None:
        if len(password.data) < 8:
            raise ValidationError(_l('Password must be at least 8 characters'))
        if not any(char.isdigit() for char in password.data):
            raise ValidationError(
                    _l('Password must contain at least 1 number'))


class DefaultUserForm(FlaskForm):
    """
        form class enables the username selection view route
    """
    username = StringField(_l("Username"), validators=[DataRequired(),
                                                       Length(min=2, max=20)])

    submit = SubmitField(_l('Sign up'))

    def validate_username(self, username: FlaskForm) -> None:
        data = models.storage.search(username.data, user_id)
        if data:
            raise ValidationError(_l('Username already taken'))


class UploadForm(FlaskForm):
    """
        image and file upload class
    """
    image = FileField('Image', validators=[
        FileRequired(message='Please select an image file.'),
        FileAllowed(['jpg', 'jpeg', 'png'],
                    message='Only JPG, JPEG, and PNG images are allowed.')
    ])
    image_name = StringField(_l("Image Name"), validators=[Optional()])

    def validate_image(self, image: FlaskForm) -> None:
        if image.data == '':
            raise ValidationError(_l('Please select an image file.'))


class LoginForm(FlaskForm):
    """
        Login form class
    """
    email = StringField(_l("Email"), validators=[DataRequired(), Email()])
    password = PasswordField(_l("Password"), validators=[DataRequired()])
    remember = BooleanField(_l("Remember Me"))
    submit = SubmitField(_l('Sign in'))

class RequestResetForm(FlaskForm):
    """
        Request reset form class
    """
    email = StringField(_l('Email'),
                        validators=[DataRequired(), Email()])
    submit = SubmitField(_l('Reset Password'))

    def validate_email(self, email: FlaskForm) -> None:
        user = models.storage.access(email.data, 'Email', user_id)
        if user is None:
            raise ValidationError(_l('''No account registered with that
                                     email address.'''))


class ResetPasswordForm(FlaskForm):
    """
        Reset password form class
    """
    password = PasswordField(_l('Password'), validators=[DataRequired()])
    confirm_password = PasswordField(_l('Confirm Password'),
                                     validators=[DataRequired(),
                                                 EqualTo('password')])
    submit = SubmitField(_l('Reset Password'))

    def validate_password(self, password: FlaskForm) -> None:
        if len(password.data) < 8:
            raise ValidationError(_l('Password must be at least 8 characters'))
        if not any(char.isdigit() for char in password.data):
            raise ValidationError(
                    _l('Password must contain at least 1 number'))


class SearchBar(FlaskForm):
    """
        search bar form class, handles all search input fields and other
        default input fields
    """
    search = StringField(_l("Search"), validators=[Optional()])
    password = PasswordField(_l('Password'), validators=[Optional()])
    old_password = PasswordField(_l('Old Password'), validators=[Optional()])
    new_password = PasswordField(_l('New Password'), validators=[Optional()])
    confirm_password = PasswordField(_l('Confirm Password'),
                                     validators=[Optional()])
    search_user = StringField(_l("Search User"), validators=[Optional()])
    submit = SubmitField(_l('Send request'))

    def validate_search(self, search: FlaskForm) -> None:
        if not re.match(r"^[a-zA-Z0-9_.,'\[\]\(\)\-\s]+$", search.data):
            raise ValidationError(_l('Invalid input parameters'))
