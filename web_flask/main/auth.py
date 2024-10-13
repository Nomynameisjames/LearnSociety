#!/usr/bin/env python3
from flask import (
    abort,
    current_app,
    flash,
    make_response,
    redirect,
    request,
    render_template,
    url_for,
    session,
)

from flask_login import login_user, current_user, logout_user, login_required
from flask_mail import Message
from flask_babel import _
from flask_wtf.csrf import validate_csrf
from wtforms import ValidationError
from werkzeug.security import generate_password_hash, check_password_hash
from google_auth_oauthlib.flow import Flow
from typing import Union, Any
from datetime import timedelta
from pathlib import Path
from dotenv import load_dotenv
from models.baseModel import user_id
from models.Update_Profile import update_redis_profile
from models.RequestModule import Notifications
from web_flask import login_manager, mail
from . import Main
from .form import (RegisterForm, LoginForm, RequestResetForm,
                   ResetPasswordForm, DefaultUserForm)
from ..Performance_logger import performance_logger
import uuid
import datetime
import jwt
import os
import models

# Google OAuth2 Configurations and settings
load_dotenv()
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
GOOGLE_CALLBACK_URL = os.getenv('GOOGLE_CALLBACK_URL')
client_secrets = os.path.join(Path(__file__).parent,
                              'client_secrets.json')
scopes = ["openid",
          "https://www.googleapis.com/auth/userinfo.profile",
          "https://www.googleapis.com/auth/userinfo.email"]


def flow() -> Flow:
    """
        function creates a flow object for google oauth2 authentication
    """
    flow = Flow.from_client_secrets_file(client_secrets_file=client_secrets,
                                         scopes=scopes,
                                         redirect_uri=GOOGLE_CALLBACK_URL)
    return flow


@login_manager.user_loader
def load_user(ID: str) -> user_id:
    """
        login manager keeps the user authenticated and stores info in session
    """
    return models.storage.access(ID, 'id', user_id)


def create_user_profile(ID: str, name: str) -> bool:
    """
        function creates a user profile for new users and saves in redisDB
    """
    search_name = models.storage.search(name, user_id)
    if search_name:
        for item in search_name:
            if name == item.User_name:
                return False
    data = [
            {ID: {
                "username": name,
                "status": "",
                "friends": [],
                "profile_picture": "",
                "friend_requests": [],
                "blocked": [],
                "messages": [],
                "chat_bot": [],
                "online_id": "",
                "last_seen": "",
                "is_active": True
                }
             }]
    
    new_user_obj = models.redis_storage.set_list_dict("Users-Profile", data)
    if new_user_obj:
        return True
    return False


def username_availability(username: str, email: str) -> bool:
    """
        function checks if username is available in the mysql database and
        returns True if available else False
    """
    all_profile = models.storage.search(username, user_id)
    if all_profile:
        for item in all_profile:
            if username == item.User_name and email != item.Email:
                return True
    return False


def new_user_token(ID: str) -> str:
    """
        function generates a jwt token for new users
    """
    from ..app import app
    token = token_payload = {
                                'user_id': ID,
                                'exp': datetime.datetime.now() + timedelta(minutes=2)
                            }
    token = jwt.encode(token_payload, app.config['SECRET_KEY'])
    return token.encode('utf-8').decode()


def verify_new_user_token(token: str) -> Union[dict, None]:
    """
        function verifies the jwt token sent to the user's email address
    """
    from ..app import app
    try:
        token_payload = jwt.decode(
                            token, 
                            app.config['SECRET_KEY'],
                            algorithms=["HS256"],
                        )
        
        my_id = token_payload['user_id']
        
    except jwt.ExpiredSignatureError:
        return None
    
    except (jwt.InvalidTokenError, KeyError):
        return None
    
    user = models.redis_storage.get_dict("temp_storage", my_id)
    
    if not user:
        return None
    
    return user


def validate_csrf_token(token: str) -> bool:
    from ..app import app
    """
        Validate the CSRF token against the app's secret key.
        Return True if valid, False otherwise.
    """
    try:
        validate_csrf(token, secret_key=app.secret_key, time_limit=None)
        return True
    except ValidationError:
        return False


def login_user_and_redirect(user: user_id, remember=False) -> Any:
    from ..app import app
    """
        Log in the user and redirect to the appropriate page sending neccessary
        auth token alongside
    """
    login_user(user, remember=remember)
    uploader = update_redis_profile(str(user.ID))
    token = jwt.encode({'user_id': user.ID, 'exp':
                       datetime.datetime.now()
                       + datetime.timedelta(minutes=120)},
                       app.config['SECRET_KEY'])
    flash(_('You are logged in!'), 'success')
    uploader.update_last_seen()
    next_page = request.args.get('next')
    response = redirect(next_page) if next_page \
        else redirect(url_for('Main.view'))
    tok = token.encode('UTF-8').decode()
    response.set_cookie('access_token', tok)
    return response


def save_user_to_db(user) -> Any:
    """
        Save a user object to the database.
        If the user already exists, log them in.
    """
    cache_file = {}
    if not user:
        return redirect(url_for('Main.signup'))
    check_email = models.storage.access(user.get("user_email"),
                                        'Email', user_id)
    ID = str(uuid.uuid4())
    if check_email:
        return login_user_and_redirect(check_email)

    elif username_availability(user.get("user_name"), user.get("user_email")):
        cache_file[ID] = {
                    'Email': user.get("user_email"),
                    'user_id': user.get("user_id")
                }
        list_item = models.redis_storage.get_dict("temp_storage", ID)
        if list_item == {}:
            models.redis_storage.set_dict("temp_storage", cache_file, ex=1800)
        flash(_("Username already taken"), 'danger')
        return redirect(url_for('Main.confirm_username', personal_id=ID))
    else:
        hashed_sub = generate_password_hash(user.get("user_id"))
        auth_user = user_id(ID=ID,
                            User_name=user.get("user_name"),
                            Email=user.get("user_email"),
                            Password=hashed_sub)
        if create_user_profile(ID, user.get("user_name")):
            models.storage.new(auth_user)
            models.storage.save()
            models.storage.close()
            return login_user_and_redirect(auth_user)
        return redirect(url_for('Main.signup'))


@Main.route('/signup', methods=['GET', 'POST'])
def signup() -> Any:
    """
        function handles the registration of new users creates an instance of
        the RegisterForm class and validates the form data, creates an instance
        of the Notifications class and validates the email address, generates
        a unique ID for the user, creates a token for the user, creates a
        verification link for the user, sends the verification link to the
        user's email address, stores the user's data in a cache file, and
        redirects the user to the signup page
    """
    form = RegisterForm()
    cache_file = {}
    mail_app = Notifications()
    ID = None
    if form.validate_on_submit():
        ID = str(uuid.uuid4())
        token = new_user_token(ID)
        # is_valid = mail_app.is_valid(form.email.data)
        
        # if not is_valid:
        #     flash(_('Invalid email address'), 'warning')
        #     return redirect(url_for('Main.signup'))
        
        url = url_for(
                        'Main.confirm_email',
                        token=token,
                        ID=ID,
                        _external=True,
                    )

        context = dict(url=url, username=form.username.data,)
        # temp_file = {
        #         'url': url,
        #         'message': "Kindly click on the link below to "\
        #                    f"complete your registration\n{url}",
        #         'subject': 'Email Verification',
        #         #'header': 'Verification',
        #         'username': form.username.data,
        #         'email': form.email.data,
        #         'id': ID
        #      }

        #sent = mail_app.send_Grid(**temp_file)
        if not mail_app.send_mail(
            "Email Verification",
            form.email.data,
            "emailFile.html",
            context
        ):
            flash(_("Use a valid/non-blacklisted email account to sign up"), "warning")
            return make_response(render_template('register.html', form=form,
                                             ID=ID))
            
        flash(_(f"An email has been sent to {form.email.data} " \
                    f"to complete your registration"), "success")
        
        password = generate_password_hash(form.password.data)
        cache_file[ID] = {
                        'Username': form.username.data,
                        'Email': form.email.data,
                        'Password': password,
                        'id':  ID
                    }
            
        prev_cache_file = models.redis_storage.get_dict("temp_storage", ID)
        if prev_cache_file == {}:
            models.redis_storage.set_dict(
                "temp_storage", cache_file, ex=1800
            )
           
        return redirect(url_for('Main.signup', ID=ID))
        
    response = make_response(render_template('register.html', form=form,
                                             ID=ID))
    return response


@Main.route('/confirm_email/<ID>/<token>', methods=['GET', 'POST'])
def confirm_email(token: str, ID: str) -> Any:
    """
        function handles the confirmation of new users by validating the token
        sent to the user and saving newly created users to the database
    """
    user = verify_new_user_token(token)
    if user is None:
        flash(_('Invalid or expired token'), 'warning')
        return redirect(url_for('Main.signup'))
    cache = models.redis_storage.get_dict('temp_storage', ID)
    if cache['id'] == ID and user:
        user = user_id(ID=cache['id'], User_name=cache['Username'],
                       Email=cache['Email'], Password=cache['Password'])
        create_user_profile(ID, cache['Username'])
        models.storage.new(user)
        models.storage.save()
        models.storage.close()
        username = {'Username': cache['Username']}
        flash(_('Account created successfully for %(user)s',
                user=username['Username']), 'success')
        
        return redirect(url_for('Main.login'))
    
    return redirect(url_for('Main.signup'))


@Main.route("/login", methods=['GET', 'POST'])
@performance_logger
def login() -> Any:
    """
        function handles the login of users by creating an instance of the
        LoginForm class and validating the form data, validates the CSRF token
        and also generates a jwt session token sent to the user's browser,
        and logs in the user if the user exists in the database
    """
    if current_user.is_authenticated:
        return redirect(url_for('Main.view'))
    form = LoginForm()
    if form.validate_on_submit():
        if validate_csrf_token(form.csrf_token.data):
            user = models.storage.access(form.email.data, 'Email', user_id)
            models.storage.close()
            if user and check_password_hash(user.Password, form.password.data):
                return login_user_and_redirect(user,
                                               remember=form.remember.data)
            else:
                flash(_(f'Login Unsuccessful. Please check username and'
                        f' password'), 'danger')
        else:
            return render_template('csrf_error.html'), 400
    return render_template('login.html', title='Login', form=form)


@Main.route('/logout')
@login_required
def logout() -> Any:
    """
        function handles the logout of users by calling the logout_user
        function from flask_login
    """
    logout_user()
    flash(_('You have been logged out.'), 'success')
    return redirect(url_for('Main.front_page'))


def send_reset_email(user: user_id) -> Any:
    try:
        token = user.get_reset_token()
        msg = Message('Password Reset Request',
                      sender='noreply@demo.com',
                      recipients=[user.Email])
        msg.body = f'''To reset your password, visit the following link:
        {url_for('Main.reset_token', token=token, _external=True)}
        If you did not make this request then simply ignore this email
        and no changes will be made.
    '''
        mail.send(msg)
    except Exception as e:
        print(e)
        return False


@Main.route('/reset', methods=['GET', 'POST'])
def reset() -> Any:
    """
        function handles the reset of user passwords by creating an instance
        of the RequestResetForm class and validating the form data, generates a
        token and sends as a password reset email to the user
    """
    if current_user.is_authenticated:
        return redirect(url_for('Main.view'))
    form = RequestResetForm()
    mail_app = Notifications()
    if form.validate_on_submit():
        token = None
        user = models.storage.access(form.email.data, 'Email', user_id)
        if user:
            token = user.get_reset_token()
        url = f"""{url_for('Main.reset_token', token=token,
                    _external=True)}"""
        mydict = {
                'url': url,
                'message': '''To reset your password, kindly visit the
                            following link:''',
                'subject': 'Password Reset Request',
                'header': f'Password Reset'
                }
        sent = mail_app.send_Grid(user, **mydict)
        models.storage.close()
        if sent:
            flash(_('''An email has been sent with instructions to reset
                  your password.'''), 'info')
            return redirect(url_for('Main.login'))
    return render_template('forget.html', title='Reset Password', form=form)


@Main.route("/reset/<token>", methods=['GET', 'POST'])
def reset_token(token: str) -> Any:
    """
        function handles the reset of user passwords by creating an instance
        of the ResetPasswordForm class and validating the form data, validates
        the token sent to user and updates the user's password
    """
    if current_user.is_authenticated:
        return redirect(url_for('Main.view'))
    user = user_id.verify_reset_token(token)
    if user is None:
        flash('That is an invalid or expired token', 'warning')
        return redirect(url_for('Main.reset'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        hash_password = generate_password_hash(form.password.data)
        user.Password = hash_password
        models.storage.save()
        models.storage.close()
        flash(_('Your password has been updated! You are now able to log in'),
              'success')
        return redirect(url_for('Main.login'))
    return render_template('reset_pass.html', form=form)


@Main.route("/google/Oauth2/users")
def google_oauth2() -> Any:
    """This method creates a new session for the user and
       generates the account verification url for users to
       authenticate with google

       Return: Returns the authentication url for user to verify
               account with google
    """
    Google_Flow = flow()
    new_session = session
    auth_url, state = Google_Flow.authorization_url()
    new_session["state"] = state
    return redirect(auth_url)


@Main.route('/Oauth/google/callback', methods=["GET", "POST"])
def callback():
    """gets googles athorization code and then exchange code for
    tokens to get the user details

    Return: the users details"""
    Google_Flow = flow()
    Google_Flow.fetch_token(authorization_response=request.url)
    credentials = Google_Flow.credentials

    user_info = jwt.decode(credentials.id_token,
                           options={"verify_signature": False})
    user = {}
    try:
        user["user_id"] = user_info["sub"]
        user["user_name"] = user_info["name"]
        user["user_email"] = user_info["email"]
    except KeyError:
        abort(404)
    response = save_user_to_db(user)
    return response


@Main.route('/confirm_username/<personal_id>', methods=['GET', 'POST'])
def confirm_username(personal_id: str) -> Any:
    usr = models.redis_storage.get_dict("temp_storage", personal_id)
    form = DefaultUserForm()
    if form.validate_on_submit():
        if not usr:
            flash(_('User not found'), 'danger')
        else:
            hashed_sub = generate_password_hash(usr.get("user_id"))
            auth_user = user_id(ID=personal_id,
                                User_name=form.username.data,
                                Email=usr.get("user_email"),
                                Password=hashed_sub)
            if create_user_profile(personal_id, form.username.data):
                models.storage.new(auth_user)
                models.storage.save()
                models.storage.close()
                flash(_('Your account has been created!', 'success'))
                response = login_user_and_redirect(auth_user)
                return response
    return render_template('select_username.html', form=form)
