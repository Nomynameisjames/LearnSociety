from flask import render_template, flash, redirect, url_for, request, make_response
from . import Main
from models.baseModel import user_id
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
import models
import uuid
import datetime
import jwt


@login_manager.user_loader
def load_user(User_id):
    return models.storage.access(User_id, 'id', user_id)


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
        sent = True #mail_app.send_Grid(None, **temp_file)
        if sent:
            flash(_(f"An email has been sent to {form.email.data} to complete your registration"), 'success')
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

    response = make_response(render_template('register.html', form=form, ID=ID))
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
            token = jwt.encode({'user_id': my_id, 'exp': 
                                datetime.datetime.utcnow() 
                                + datetime.timedelta(minutes=60)},
                               app.config['SECRET_KEY'])
            flash(_('You are logged in!'), 'success')
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
                'url': url,
                'message': f'''To reset your password, kindly visit the following link:''',
                'subject': 'Password Reset Request',
                'header': f'Password Reset'
                }
        sent = mail_app.send_Grid(user, **mydict)
        #send_reset_email(user)
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
