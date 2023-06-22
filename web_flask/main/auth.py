from flask import (flash, make_response, redirect,
                   render_template, request, session, url_for)
from . import Main
from models.baseModel import user_id
from models.Update_Profile import update_redis_profile
from .form import RegisterForm, LoginForm, RequestResetForm, ResetPasswordForm
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, current_user, logout_user, login_required
from web_flask import login_manager, mail
from flask_mail import Message
from models.RequestModule import Notifications
from ..Performance_logger import performance_logger
from datetime import timedelta
from flask_wtf.csrf import validate_csrf
from wtforms import ValidationError
from flask_babel import _
from pathlib import Path, os
from google_auth_oauthlib.flow import Flow
import models
import uuid
import datetime
import jwt


os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

try:
    GOOGLE_CALLBACK_URL = os.getenv('GOOGLE_CALLBACK_URL')

except KeyError as err:
    abort(404)

client_secrets = os.path.join(Path(__file__).parent,
                              'client_secrets.json')

scopes = ["openid",
          "https://www.googleapis.com/auth/userinfo.profile",
          "https://www.googleapis.com/auth/userinfo.email"]

flow = Flow.from_client_secrets_file(client_secrets_file=client_secrets,
                                     scopes=scopes,
                                     redirect_uri=GOOGLE_CALLBACK_URL)


@login_manager.user_loader
def load_user(User_id):
    return models.storage.access(User_id, 'id', user_id)


def create_user_profile(ID, name):
    """
        function creates a user profile for new users and saves in redisDB
    """
    data = [{ID: {
                    "username": name,
                    "status": "",
                    "friends": [],
                    "friend_requests": [],
                    "blocked": [],
                    "profile_pic": "",
                    "messages": [{
                                    "sender": "",
                                    "message": [],
                                    "time": []
                                }],
                    "chat_bot": [],
                    "last_seen": ""
                }}]
    models.redis_storage.set_list_dict("Users-Profile", data)
    return True


def new_user_token(ID):
    """
        function generates a jwt token for new users
    """
    from ..app import app
    token = token_payload = {'user_id': ID, 'exp': datetime.datetime.utcnow()
                             + timedelta(minutes=2)}
    token = jwt.encode(token_payload, app.config['SECRET_KEY'])
    return token.encode('utf-8').decode()


def verify_new_user_token(token):
    """
        function verifies the jwt token sent to the user's email address
    """
    from ..app import app
    try:
        token_payload = jwt.decode(token, app.config['SECRET_KEY'],
                                   algorithms=["HS256"])
        my_id = token_payload['user_id']
    except jwt.ExpiredSignatureError:
        return None
    except (jwt.InvalidTokenError, KeyError):
        return None
    user = models.redis_storage.get_list(my_id)
    if not user:
        return None
    return user


@Main.route('/signup', methods=['GET', 'POST'])
def signup():
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
    mail_app = Notifications()
    ID = None
    if form.validate_on_submit():
        ID = str(uuid.uuid4())
        token = new_user_token(ID)
        is_valid = mail_app.is_valid(form.email.data)
        if not is_valid:
            flash(_('Invalid email address'), 'warning')
            return redirect(url_for('Main.signup'))
        url = f"""{url_for('Main.confirm_email', token=token, ID=ID,
                    _external=True)}"""
        temp_file = {
                'url': url,
                'message': f'''Kindly click on the link below to
                                complete your registration''',
                'subject': 'Email Verification',
                'header': f'Verification',
                'username': form.username.data,
                'email': form.email.data,
                'id': ID
                }
        print(url)
        sent = True  # mail_app.send_Grid(None, **temp_file)
        if sent:
            flash(_(f"An email has been sent to {form.email.data}"
                    "to complete your registration"), 'success')
            password = generate_password_hash(form.password.data)
            cache_file = {
                    'Username': form.username.data,
                    'Email': form.email.data,
                    'Password': password,
                    'id':  ID
                    }
            list_item = models.redis_storage.get_list(ID)
            list_item.append(cache_file)
            models.redis_storage.set_dict(ID, list_item)
            return redirect(url_for('Main.signup', ID=ID))

    response = make_response(render_template('register.html',
                             form=form, ID=ID))
    return response


@Main.route('/confirm_email/<ID>/<token>', methods=['GET', 'POST'])
def confirm_email(token, ID):
    """
        function handles the confirmation of new users by validating the token
        sent to the user and saving newly created users to the database
    """
    user = verify_new_user_token(token)
    if user is None:
        flash('Invalid or expired token', 'warning')
        return redirect(url_for('Main.signup'))
    form = models.redis_storage.get_list(ID)
    for i in form:
        if i['id'] == ID and user:
            user = user_id(id=i['id'], User_name=i['Username'],
                           Email=i['Email'], Password=i['Password'])
            create_user_profile(ID, i['Username'])
            models.storage.new(user)
            models.storage.save()
            models.storage.close()
            username = {'Username': i['Username']}
            flash(_('Account created successfully for %(user)s',
                    user=username['Username']), 'success')
            models.redis_storage.delete(ID)
            return redirect(url_for('Main.login'))
    return redirect(url_for('Main.signup'))


@Main.route("/login", methods=['GET', 'POST'])
@performance_logger
def login():
    """
        function handles the login of users by creating an instance of the
        LoginForm class and validating the form data, validates the CSRF token
        and also generates a jwt session token sent to the user's browser,
        and logs in the user if the user exists in the database
    """
    from ..app import app
    if current_user.is_authenticated:
        return redirect(url_for('Main.view'))
    form = LoginForm()
    if form.validate_on_submit():
        try:
            validate_csrf(form.csrf_token.data, secret_key=app.secret_key,
                          time_limit=None)
        except ValidationError:
            # Handle invalid CSRF token
            return render_template('csrf_error.html'), 400
        user = models.storage.access(form.email.data, 'Email', user_id)
        models.storage.close()
        if user and check_password_hash(user.Password, form.password.data):
            login_user(user, remember=form.remember.data)
            my_id = current_user.id
            uploader = update_redis_profile(my_id)
            token = jwt.encode({'user_id': my_id, 'exp':
                                datetime.datetime.utcnow()
                                + datetime.timedelta(minutes=60)},
                               app.config['SECRET_KEY'])
            flash(_('You are logged in!'), 'success')
            uploader.update_last_seen()
            next_page = request.args.get('next')
            response = redirect(next_page) if next_page\
                            else redirect(url_for('Main.view'))
            tok = token.encode('UTF-8').decode()
            response.set_cookie('access_token', tok)
            return response
        else:
            flash(_('Login Unsuccessful. Please check username and password'),
                  'danger')
    return render_template('login.html', title='Login', form=form)


@Main.route('/logout')
@login_required
def logout():
    """
        function handles the logout of users by calling the logout_user
        function from flask_login
    """
    logout_user()
    flash(_('You have been logged out.'), 'success')
    return redirect(url_for('Main.front_page'))


def send_reset_email(user):
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
        return str(e)


@Main.route('/reset', methods=['GET', 'POST'])
def reset():
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
        user = models.storage.access(form.email.data, 'Email', user_id)
        token = user.get_reset_token()
        url = f"""{url_for('Main.reset_token', token=token,
                    _external=True)}"""
        mydict = {
                    "url": url,
                    "message": "To reset your password, kindly visit"
                               "the following link:",
                    "subject": "Password Reset Request",
                    "header": "Password Reset"
                }
        sent = mail_app.send_Grid(user, **mydict)
        # send_reset_email(user)
        models.storage.close()
        if sent:
            flash(_('''An email has been sent with instructions to reset
                  your password.'''), 'info')
            return redirect(url_for('Main.login'))
    return render_template('forget.html', title='Reset Password', form=form)


@Main.route("/reset/<token>", methods=['GET', 'POST'])
def reset_token(token):
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


def save_user_to_db(user):
    """saves a user object to the database"""

    if not user:
        return redirect(url_for('Main.signup'))
    auth_user = None
    check_email = models.storage.find_user_by(Email=user.get("user_email"))

    if not check_email:
        hashed_sub = generate_password_hash(user.get("user_id"))
        auth_user = user_id(id=str(uuid.uuid4()),
                            User_name=user.get("user_name"),
                            Email=user.get("user_email"),
                            Password=hashed_sub)

        models.storage.new(auth_user)
        models.storage.save()
        models.storage.close()


    else:
        login_user(check_email)
        return check_email

    login_user(auth_user)
    return auth_user


@Main.route("/google/Oauth2/users")
def google_oauth2():
    """This method creates a new session for the user and
       generates the account verification url for users to
       authenticate with google

       Return: Returns the authentication url for user to verify
               account with google
    """

    new_session = session

    auth_url, state = flow.authorization_url()
    new_session["state"] = state
    return redirect(auth_url)


@Main.route('/Oauth/google/callback', methods=["GET", "POST"])
def google_oauth2_callback():
    """gets googles athorization code and then exchange code for
    tokens to get the user details

    Return: the users details"""

    flow.fetch_token(authorization_response=request.url)
    credentials = flow.credentials

    user_info = jwt.decode(credentials.id_token,
                           options={"verify_signature": False})
    user = {}
    try:
        user["user_id"] = user_info["sub"]
        user["user_name"] = user_info["name"]
        user["user_email"] = user_info["email"]

    except KeyError:
        abort(404)

    save_user_to_db(user)
    return redirect(url_for("Main.view"))
