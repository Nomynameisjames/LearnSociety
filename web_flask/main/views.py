from flask import (Flask, render_template, abort, url_for, redirect,
                    flash, request, jsonify, make_response)
from models.Schedule import Create_Schedule
from models.checker import Checker
from models.Update_Profile import update_redis_profile
from werkzeug.utils import secure_filename
from flask_login import login_required, current_user
from pyuploadcare import Uploadcare
from ..Performance_logger import performance_logger
from . import Main
from .form import SearchBar, UploadForm

#from .. import cache
from uuid import uuid4
import models
import os

"""
    This file contains all the routes for the application
    this enables user to query the database to view Schedules
    based on the status of the task
"""
quiz_data = {}
auto = False
course = None

def Upload_file(file):
    pub_key = os.environ.get('UploadCare_PUBLIC_KEY')
    secret_key = os.environ.get('UploadCare_SECRET_KEY')
    try:
        uploadcare = Uploadcare(public_key=pub_key, secret_key=secret_key)
        ucare_file = uploadcare.upload(file)
        return ucare_file.cdn_url
    except Exception as e:
        print(f"\nfollwing error occured: {e}\n")
        return

def get_display_picture(user_id):
    """ gets the users display picture from the database """
    uploader = update_redis_profile(user_id)
    dp = uploader.get
    return dp.get('profile_picture')

#@cache.memoize(timeout=200, make_name=lambda user_id: 'get_last_update_time_v1_uid' + str(user_id))
#def get_last_update_time(user_id):
#    bot = Create_Schedule(user_id)
#    dic = bot.View(user_id)
#    last_update = ''
#    recent_delta = timedelta(hours=1)
#    recent_time = datetime.now() - recent_delta
#    last_update = [value for key, value in dic.items() if key == 'Created'
#                   and value is not None and datetime.strptime(value,
#                                        '%Y-%m-%d %H:%M:%S') >= recent_time]
#    
#    if last_update:
#        last_update = last_update
#    else:
#        last_update = ''
#
#    return last_update

@Main.route('/')
def front_page():
    """
        This is the landing page of the application
    """
    return render_template('landing_page.html')


@Main.route('/about')
def about():
    """
        about page of the application
    """
    return render_template('about.html')


@Main.route('/tasks/<status>',  methods=['GET'])
@login_required
#@cache.cached(timeout=100)
def Tasks(status: str):
    """
        This route enables user to view status of tasks
    """
    my_id = current_user.id
    user = current_user.User_name
    form = SearchBar()
    if not my_id:
        flash('You need to be logged in to view this page', 'danger')
        return redirect(url_for('Main.login'))
    bot = Create_Schedule(my_id)
    if auto:
        dic = bot.View(my_id, status, course)
        return render_template('task_status.html', data=dic, form=form,
                               state=auto, user=user)
    else:
        dic = bot.View(my_id, status)
        return render_template('task_status.html', data=dic, form=form,
                               user=user)

@Main.route('/View', methods=['GET'])
@login_required
@performance_logger
def view():
    """
        This route enables user to view all tasks, also uses the auto global
        variable to determine if the user is searching for a customised task
        or autmoated task
    """
    global auto
    form = SearchBar()
    user_id = current_user.id
    user = current_user.User_name
    if not user_id:
        flash('You need to be logged in to view this page', 'danger')
        return redirect(url_for('Main.login'))
    bot = Create_Schedule(user_id)
    dic = bot.View(user_id)
    #cache_key = f'user_{user_id}_{user}'
    #cached_data = models.redis_storage.get_dict(cache_key)
    #if cached_data:
    #    data = cached_data
    #else:
    #models.redis_storage.set_dict(cache_key, data, ex=200)
    auto = False
    response = make_response(render_template('index.html', data=dic,
                                             status=auto, user=user,
                           form=form))
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    return response

@Main.route('/quiz')
@login_required
@performance_logger
def quiz():
    """
        This route enables user to take a quiz and serves each question
        in the quiz_data global variable
    """
    global quiz_data # declare global variable
    ID = current_user.id
    user = current_user.User_name
    if not ID:
        flash('You need to be logged in to view this page', 'danger')
        return redirect(url_for('Main.login'))
    if auto:
        bot = Checker(ID, course)
        data_id = bot.task_ID
    else:
        bot = Checker(ID)
        data_id = bot.task_ID
    if not bot.task or not data_id:
        return f"Sorry, there are no tasks available at the moment."
    if not quiz_data: # check if global variable is not empty
        dic = bot.Question()
        quiz_data = dic # store results in global variable
        return render_template('quiz.html', data=dic, data_ID=data_id,
                               user=user)
    else:
        return render_template('quiz.html', data=quiz_data, data_ID=data_id,
                               user=user)

@Main.route('/auto_dash', methods=['GET'])
@login_required
@performance_logger
def dashboard():
    """
        This route enables user to view the auto schedule dashboard
        also updates specific tasks a user views by updating the auto
        global variable and the course global variable
    """
    global auto, course
    ID = current_user.id
    user = current_user.User_name
    form = SearchBar()
    files = None
    if not ID:
        flash('You need to be logged in to view this page', 'danger')
        return redirect(url_for('Main.login'))
    data = models.storage.view(ID)[0].get(ID)
    if data:
        files = {
                "Python" : data.auto_schedules,
                "Javascript" : data.JScourse,
                "React" : data.Reactcourse,
                "C" : data.C_course
            }
    course = request.args.get('myID')
    doc = {}
    key = None
    #cache_key = f'user_{ID}_{course}'
    #cached_data = models.redis_storage.get_dict(cache_key)
    if course in files:
       # data = Create_Schedule(ID)
        doc =  files.get(course)
    else:
        abort(404, description="Resource not found")
    #if cached_data:
    #    doc = cached_data
    #else:
    #    doc = files.get(course)
    #    models.redis_storage.set_dict(cache_key, doc, ex=200)
    if doc:
        key = [i for i in doc if i.user_ID == ID]
    if key:
        auto = True
        return render_template('auto_dash.html', data=doc, status=auto,
                               form=form, user=user)
    else:
        return render_template('auto_reg.html', form=form)


@Main.route('/articles', methods=['GET'])
@login_required
@performance_logger
def articles():
    """
        This route enables user library page
    """
    ID = current_user.id
    form = SearchBar()
    if not ID:
        flash('You need to be logged in to view this page', 'danger')
        return redirect(url_for('Main.login'))
    if auto and course == 'Python':
        return render_template('articles.html', status=auto, form=form)
    elif auto and course == 'Javascript':
        return render_template('JSarticles.html', status=auto, form=form)
    elif auto and course == 'React':
        return render_template('Reactarticles.html', status=auto, form=form)
    elif auto and course == 'C':
        return render_template('C_articles.html', status=auto, form=form)
    else:
        return render_template('auto_reg.html', form=form)


@Main.route('/community', methods=['GET', 'POST'])
@login_required
@performance_logger
def ChatRoom():
    """
        This route enables user to view the chat room
    """
    username = current_user.User_name
    community = []
    uploader = update_redis_profile(current_user.id)
    display_picture = get_display_picture(current_user.id)
    Form = UploadForm()
    form = SearchBar()
    if Form.validate_on_submit():
        images = Form.image.data
        image_desc = Form.image_name.data
        if images and image_desc == "User":
            data = Upload_file(images)
            if data:
                uploader.save_profile_picture(data)
                flash('Profile picture updated', 'success')
                return redirect(url_for('Main.ChatRoom'))
            else:
                flash('Profile picture not updated', 'danger')
                return redirect(url_for('Main.ChatRoom'))
    get_community = models.redis_storage.get_list_dict('community')
    if get_community:
        community = get_community
    return render_template('chatRoom.html', Form=Form, form=form, communities=community,
                           user=username, dp=display_picture)

@Main.route('/ChatRoom/<room_id>', methods=['GET', 'POST'])
@login_required
@performance_logger
def ChatRoomID(room_id):
    """
        This route enables user to view the chat room
    """
    if room_id is None:
        return redirect(url_for('Main.ChatRoom'))
    username = current_user.User_name
    ID = current_user.id
    Form = UploadForm()
    chat_history = []
    community = []
    groupinfo = {}
    joinroom = []
    form = SearchBar()
    get_community = models.redis_storage.get_list_dict('community')
    if get_community:
        community = get_community
        for item in get_community:
            for key, value in item.items():
                if key == room_id:
                    groupinfo = value
                    chat_history = value.get('chat')
                    joinroom = groupinfo.get("users")
    if groupinfo is None or username not in joinroom:
        flash('You are not a member of this group get group code to join',
              'danger')
        return redirect(url_for('Main.ChatRoom'))
    rendered_template = render_template('chatRoomPage.html', form=form,
                                            communities=community,
                                            groupinfo=groupinfo,
                                            user=username, ID=ID,
                                            Form=Form, dp=get_display_picture(ID),
                                            chats=chat_history)
    response = make_response(rendered_template)
    return response

@Main.route('/friends/', methods=['GET', 'POST'])
@login_required
@performance_logger
def friends_page():
    """
        This route enables user to view the friends page
    """
    username = current_user.User_name
    ID = current_user.id
    community = []
    form = SearchBar()
    Form = UploadForm()
    display_picture = get_display_picture(current_user.id)
    get_community = models.redis_storage.get_list_dict('community')
    if get_community:
        community = get_community
    return render_template('friendsPage.html', form=form, Form=Form, dp=display_picture,
                           communities=community, user=username, ID=ID)
