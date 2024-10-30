from flask import (render_template, abort, url_for, redirect,
                   flash, request, make_response)
from flask_login import login_required, current_user
from pyuploadcare import Uploadcare
from typing import Union, Any
from dotenv import load_dotenv
from models.Schedule import Create_Schedule
from models.checker import Checker
from models.Update_Profile import update_redis_profile
from models.community_data import CommunityData
from ..Performance_logger import performance_logger
from .. import cache
from . import Main
from .form import SearchBar, UploadForm
import os
import models

"""
    This file contains all the routes for the application
    this enables user to query the database to view Schedules
    based on the status of the task
"""
load_dotenv()
auto = False
course = None


def Upload_file(file: str) -> Union[str, None]:
    """
        uploads file to uploadcare and returns the cdn url
    """
    pub_key = os.getenv('UploadCare_PUBLIC_KEY')
    secret_key = os.getenv('UploadCare_SECRET_KEY')
    try:
        uploadcare = Uploadcare(public_key=pub_key, secret_key=secret_key)
        ucare_file = uploadcare.upload(file)
        print(ucare_file.cdn_url)
        return ucare_file.cdn_url
    except Exception as e:
        print(f"\nfollwing error occured: {e}\n")
        return


def get_display_picture(user_id: str, file: str) -> Union[str, None]:
    """
        gets the users display picture or file from the redis database
    """
    uploader = update_redis_profile(user_id)
    dp = uploader.get
    return dp.get(str(file))


@Main.route('/')
def front_page() -> Any:
    """
        landing page view route of application
    """
    return render_template('landing_page.html')


@Main.route('/about')
def about() -> Any:
    """
        about page  view route of application
    """
    return render_template('about.html')


@Main.route('/tasks/<status>',  methods=['GET'])
@login_required
@cache.cached(timeout=200)
def Tasks(status: str) -> Any:
    """
        This route enables user to view status of tasks
    """
    my_id = current_user.ID
    form = SearchBar()
    if not my_id:
        flash('You need to be logged in to view this page', 'danger')
        return redirect(url_for('Main.login'))
    bot = Create_Schedule(my_id)
    if auto:
        dic = bot.View(status, course)
        return render_template('task_status.html', data=dic, form=form,
                               state=auto)
    else:
        dic = bot.View(status, None)
        return render_template('task_status.html', data=dic, form=form)


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
    user_id = current_user.ID
    if not user_id:
        flash('You need to be logged in to view this page', 'danger')
        return redirect(url_for('Main.login'))
    bot = Create_Schedule(user_id)
    dic = bot.View()
    auto = False
    response = make_response(render_template('index.html', data=dic,
                                             status=auto, form=form))
    return response


@Main.route('/quiz')
@login_required
@performance_logger
@cache.cached(timeout=500)
def quiz() -> Any:
    """
        This route enables user to take a quiz and serves each question
        in the quiz_data global variable
    """
    ID = current_user.ID
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
        flash('Sorry, there are no tasks available at the moment.', 'danger')
        return redirect(url_for('Main.view'))
    dic = bot.Question()
    return render_template('quiz.html', data=dic, data_ID=data_id)


@Main.route('/auto_dash', methods=['GET'])
@login_required
@performance_logger
def dashboard() -> Any:
    """
        This route enables user to view the auto schedule dashboard
        also updates specific tasks a user views by updating the auto
        global variable and the course global variable
    """
    global auto, course
    ID = current_user.ID
    form = SearchBar()
    user_file = Create_Schedule(ID)
    files = None
    if not ID:
        flash('You need to be logged in to view this page', 'danger')
        return redirect(url_for('Main.login'))
    files = user_file.coursefile
    course = request.args.get('myID')
    doc = {}
    key = None
    if course in files:
        doc = files.get(course)
    else:
        abort(404, description="Resource not found")
    if doc:
        key = [i for i in doc if i.user_ID == ID]
    if key:
        auto = True
        return render_template('auto_dash.html', data=doc, status=auto,
                               form=form)
    else:
        return render_template('auto_reg.html', form=form)


@Main.route('/articles', methods=['GET'])
@login_required
@performance_logger
def articles() -> Any:
    """
        This route enables user library page
    """
    ID = current_user.ID
    form = SearchBar()
    if not ID:
        flash('You need to be logged in to view this page', 'danger')
        return redirect(url_for('Main.login'))
    if auto and course == 'Python':
        return render_template('Python_library.html', status=auto, form=form)
    elif auto and course == 'Javascript':
        return render_template('Javascript_library.html', status=auto,
                               form=form)
    elif auto and course == 'React':
        return render_template('React_library.html', status=auto, form=form)
    elif auto and course == 'C':
        return render_template('The_C_library.html', status=auto, form=form)
    else:
        return render_template('auto_reg.html', form=form)


@Main.route('/community', methods=['GET', 'POST'])
@login_required
@performance_logger
def ChatRoom() -> Any:
    """
        This route enables user to view the chat room
    """
    uploader = update_redis_profile(current_user.ID)
    display_picture = get_display_picture(current_user.ID, "profile_picture")
    status = get_display_picture(current_user.ID, "status")
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
    data = CommunityData()
    return render_template('chatRoom.html', Form=Form, form=form,
                           communities=data.get_all_community,
                           dp=display_picture, status=status)


@Main.route('/ChatRoom/<room_id>', methods=['GET', 'POST'])
@login_required
@performance_logger
def ChatRoomID(room_id: str) -> Any:
    """
        This route enables user to view the chat room
    """
    if room_id is None:
        return redirect(url_for('Main.ChatRoom'))
    ID = current_user.ID
    Form = UploadForm()
    communities = CommunityData(room_id)
    dp = get_display_picture(ID, "profile_picture")
    group_info = communities.get_community
    join_room = communities.get_members()
    members_profile = communities.get_members_profile(current_user.User_name)
    if group_info is None or current_user.User_name not in join_room:
        flash('You are not a member of this group get group code to join',
              'danger')
        return redirect(url_for('Main.ChatRoom'))
    rendered_template = render_template(
            'chatRoomPage.html',
            communities=communities.get_all_community,
            groupinfo=group_info,
            Form=Form,
            chats=communities.get_chat_history(),
            dp=dp,
            members=members_profile
            )
    response = make_response(rendered_template)
    return response


@Main.route('/friends/', methods=['GET', 'POST'])
@login_required
@performance_logger
def friends_page() -> Any:
    """
        This route enables user to view the friends page
    """
    ID = current_user.ID
    all_user = update_redis_profile(current_user.ID)
    user_data = all_user.get
    friends = user_data.get('friend_requests')
    community = []
    form = SearchBar()
    Form = UploadForm()
    if friends is None:
        num_friends = 0
    else:
        num_friends = len(friends)
    display_picture = get_display_picture(current_user.ID, "profile_picture")
    get_community = models.redis_storage.get_list_dict('community')
    if get_community:
        community = get_community
    return render_template(
            'friendsPage.html',
            form=form,
            Form=Form,
            dp=display_picture,
            communities=community,
            status=get_display_picture(ID, "status"),
            friends_request=num_friends
            )


@Main.route('/friends/<friend_id>', methods=['GET', 'POST'])
@login_required
@performance_logger
def friends_chat(friend_id) -> Any:
    """
        route creates a page that displays a users conversation with a friend
    """
    user_id = current_user.ID
    Form = UploadForm()
    user_data = update_redis_profile(user_id)
    friends_data = update_redis_profile.find_user(None, friend_id)
    communities = models.redis_storage.get_list_dict('community')
    dp = get_display_picture(user_id, "profile_picture")
    status = get_display_picture(user_id, "status")
    user_info = user_data.get
    chat_history = user_info.get('messages')
    conversation = []
    friends_list = user_info.get('friends')
    if chat_history is not None and friend_id in friends_list:
        for item in chat_history:
            if friend_id in item.get("sender"):
                conversation = item.get("messages")
                break
    else:
        conversation = []
    if friends_data and friends_data["profile_picture"] is None:
        friends_data["profile_picture"] = os.environ["DEFAULT_PICTURE"]
    print(dp)
    return render_template('friendsChat.html', chats=conversation,
                           dp=dp, communities=communities,
                           status=status, friend_info=friends_data,
                           Form=Form)
