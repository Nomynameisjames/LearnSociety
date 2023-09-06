#!/usr/bin/python3
from flask import abort, jsonify, request
from flask_login import current_user
from dotenv import load_dotenv
from datetime import datetime
from models.checker import Checker
from models.Update_Profile import update_redis_profile
from models.community_data import CommunityData
from web_flask.main.views import Upload_file
from api.v1.main import main_app
from .tasks import token_required, limit_request_frequency
from web_flask.Performance_logger import performance_logger
from .update_data import Settings, create_community
import yaml
import functools
import os


load_dotenv()


@main_app.route('/chatbot/', methods=['GET', 'POST'])
@token_required
@limit_request_frequency(num_requests=3, per_seconds=10)
@performance_logger
def help(current_user: current_user) -> jsonify:
    """
        enables the chat bot functionality by creating an instance of the
        checker class and calling the help method to process the user's request
        to the openAI api
    """
    ID = current_user.ID
    bot = Checker(ID)
    uploader = update_redis_profile(ID)
    req_data = request.get_json()
    if request.method == 'POST':
        for text in req_data.values():
            res = bot.Help(text)
            message = {
                "text": res,
                "time": datetime.utcnow().strftime("%-d %b %Y %I:%M:%S%p"),
                "picture": os.getenv('CHAT_BOT')
            }
            return jsonify(message), 200
    if request.method == 'DELETE':
        uploader.clear_chatbot_history()
        return jsonify({"message": "successfully removed"}), 200
    else:
        abort(400, description='Failed to perform request')


@main_app.route('/quiz', methods=['GET', 'POST'])
@token_required
@limit_request_frequency(num_requests=3, per_seconds=10)
@performance_logger
# @cache.cached(timeout=500)
def quiz(current_user: current_user) -> jsonify:
    """
        function handles the quiz functionality which gets the quiz answers
        from the user and sends them to the openAI api for processing using the
        checker class static method _invoke_chatbot, validate and updates the
        users average score in the mysql database using the static method
        check_answers
    """
    ID = current_user.ID
    quiz_answers = request.get_json()
    Key = None
    Value = {}
    test_sheet = {}
    for k, v in quiz_answers.items():
        Key = k
        Value = v
    if Key is None:
        abort(404, description='Core credentials not found')
    new_key = list(Value.keys())
    new_key = ''.join(new_key).split('.').pop(0)
    if request.method == 'POST':
        if quiz_answers is None:
            abort(404, description='invalid request')
        else:
            for _, values in Value.items():
                test_sheet[Key] = dict(zip(new_key, values))
                data = Checker._invoke_chatbot(test_sheet)
                if Key and isinstance(data, dict):
                    Checker.check_answers(data, ID, int(Key))
                message = {Key: data}
                with open('QuizFile.yaml', 'a') as f:
                    yaml.dump(message, f)
                return jsonify(message), 201
            else:
                return jsonify({"message": "Quiz data already present"}), 204
    if request.method == 'GET':
        with open('QuizFile.yaml', 'r') as f:
            file = yaml.safe_load(f)
        if file is None:
            abort(404, description='Resource not found')
        else:
            return jsonify({"message": file}), 200


@main_app.route('/settings/', methods=['POST', 'DELETE'])
@token_required
@limit_request_frequency(num_requests=20, per_seconds=10)
@performance_logger
def settings(current_user: current_user) -> jsonify:
    """
        function handles the user settings functionality which enables the user
        to update their profile, save chat history and send confirmation code
        to their email address for verification purposes
    """
    data = request.get_json()
    option = data.get('option')
    update_func = Settings(current_user)
    options = {
            'email': update_func.send_user_notification,
            'confirmation': update_func.verify_confirmation_code,
            'checkBox': update_func.update_save_history,
            'chatHistory': update_func.delete_chat_history,
            'deleteCourse': update_func.delete_auto_course,
            'deleteAccount': update_func.delete_account
        }

    if request.method == 'POST':
        if data is None and option not in options:
            abort(404, 'invalid credentials')
        function = options[option]
        Request_obj = function()
        if Request_obj:
            return jsonify({"message": Request_obj}), 200

    elif request.method == 'DELETE':
        if data is None and option not in options:
            abort(404, description='record not found')
        function = options[option]
        Request_obj = function()
        if Request_obj:
            return jsonify({"message": Request_obj}), 200
    else:
        abort(400, description='invalid request')


@main_app.route('/settings/', methods=['PUT'])
@token_required
@limit_request_frequency(num_requests=3, per_seconds=60)
@performance_logger
def Update_user_profile(current_user: current_user) -> jsonify:
    """
        function creates an instance of the Settings class and calls the
        update methods based on the request data passed in the request body
    """
    data = request.get_json()
    option = data.get('option')
    update_func = Settings(current_user)
    options = {
        'username': update_func.update_username,
        'email': update_func.update_email,
        'course_tempo': update_func.update_course_tempo,
        'contact': update_func.update_contact,
        'password': update_func.update_password,
        "status": update_func.update_status
    }

    if request.method == 'PUT':
        if data is None and option not in options:
            abort(404, 'invalid credentials')
        function = options[option]
        Obj = function()
        if Obj:
            return jsonify({"message": "successfully updated"}), 200
        else:
            abort(404, 'invalid credentials')


@main_app.route('/community/', methods=['POST'])
@token_required
@limit_request_frequency(num_requests=3, per_seconds=10)
@performance_logger
def community(current_user: current_user) -> jsonify:
    """
        function handles the community functionality which enables the user
        to create a room
    """
    ID = current_user.ID
    username = current_user.User_name
    room = request.form.get('room')
    description = request.form.get('description')
    image = request.files.get('image')
    image_file = Upload_file(image)
    new_room = {
            'name': room,
            'description': description,
            'admin': username,
            "group_picture": image_file
            }
    Community = create_community(ID, **new_room)
    if Community:
        return jsonify({"message": "successfully created"}), 201
    else:
        return jsonify({"message": "Can't create room"}), 400


@main_app.route('/community/', methods=['PUT', 'DELETE'])
@token_required
@limit_request_frequency(num_requests=20, per_seconds=60)
@performance_logger
def Update_community(current_user: current_user) -> jsonify:
    """
        function handles the community functionality which enables the admin
        user to clear a room chat history
    """
    username = current_user.User_name
    data = request.get_json()
    room_code = data.get('room_code')
    community = CommunityData()
    payload = {
        'description': data.get('description'),
        'new_name': data.get('new_name')
        }
    if request.method == 'PUT':
        if community.edit_community_profile(room_code, username, **payload):
            return jsonify({"message": "successfully updated room info"}), 200
        else:
            return jsonify({
                "description":
                "you don't have admin privileges to modify room data"
                }), 400
    elif request.method == 'DELETE':
        if community.edit_community_profile(room_code, username):
            return jsonify({"message": "successfully deleted"}), 200
        else:
            return jsonify({
                "description":
                "you don't have admin privileges to modify room data"}), 400
    else:
        abort(400, description='invalid request')


@main_app.route('/friends/<option>', methods=['GET', 'PUT', 'DELETE'])
@token_required
@limit_request_frequency(num_requests=50, per_seconds=10)
@performance_logger
@functools.lru_cache(maxsize=128)
def friends(current_user: current_user, option: str) -> jsonify:
    """
        Function handles the friends functionality which enables the user
        to add friends and view their friends list.
    """
    ID = current_user.ID
    user_data = update_redis_profile(ID)
    friends_list = []
    if request.method != 'GET' and request.method != 'PUT'\
            and request.method != 'DELETE':
        abort(400, description='Invalid request')
    user = user_data.get
    if option == "All":
        friends_list = user_data.view_all_friends()
        if friends_list:
            return jsonify({"message": friends_list}), 200
        else:
            return jsonify({"message": "you have no friends"}), 200
    elif option == "Pending":
        friends_list = []
        pending_request = user.get("friend_requests")
        if pending_request:
            for item in pending_request:
                friends_list.append(update_redis_profile.find_user(None, item))
            return jsonify({"message": friends_list}), 200
        else:
            return jsonify({"message": "you have no pending requests"}), 200
    elif option == "Blocked":
        blocked_list = []
        blocked_user_id = user.get("blocked")
        if blocked_user_id:
            for item in blocked_user_id:
                blocked_list.append(update_redis_profile.find_user(None, item))
            return jsonify({"message": blocked_list}), 200
        else:
            return jsonify({"message": "you have no blocked users"}), 200
    elif option == "block" and request.method == "PUT":
        payload = request.get_json()
        user_id = payload.get("user_id")
        if user_id:
            blocked_user = user_data.block_user(user_id)
            if blocked_user:
                return jsonify(
                        {"message": "successfully blocked this user"
                         }), 200
    elif option == "unblock" and request.method == "PUT":
        payload = request.get_json()
        user_id = payload.get("user_id")
        if user_id:
            unblocked_user = user_data.unblock_user(user_id)
            if unblocked_user:
                return jsonify(
                        {"message": "successfully unblocked this user"}
                        ), 200
    elif option == "clear" and request.method == "DELETE":
        payload = request.get_json()
        user_id = payload.get("friend_id")
        if user_id:
            cleared_chat = user_data.delete_user_chat_history(user_id)
            if cleared_chat:
                return jsonify(
                        {"message": "successfully cleared chat history"}
                        ), 200
    else:
        abort(400, description='Invalid request')


@main_app.route('/friends/request/<user>', methods=['POST'])
@token_required
@limit_request_frequency(num_requests=50, per_seconds=10)
@performance_logger
@functools.lru_cache(maxsize=128)
def add_friends(current_user: current_user, user: str) -> jsonify:
    """
        Function handles the friends functionality which enables the user
        to add friends and view friends list.
    """
    ID = current_user.ID
    user_data = update_redis_profile(ID)
    if request.method != 'POST':
        abort(400, description='Invalid request')
    if not user:
        return jsonify({"message": "Please enter a username"}), 400
    if user == current_user.User_name:
        return jsonify({"message": "😄 You can't add yourself"}), 400
    request_data = update_redis_profile.find_user(user, None)
    if request_data is None:
        return jsonify({"message": "User not found"}), 400
    new_friend_id = request_data.get("id")
    current_user_data = user_data.get
    friend_requests = current_user_data.get("friend_requests", [])
    friends_list = current_user_data.get("friends", [])
    if new_friend_id in friends_list:
        return jsonify({
            "message": "You are already friends with this user"
            }), 400
    elif new_friend_id in friend_requests:
        return jsonify({"message": "You already sent a friend request"}), 400
    elif new_friend_id in current_user_data.get("blocked", []):
        return jsonify({"message": "You have blocked this user"}), 400
    elif update_redis_profile.send_friend_request(user, ID):
        return jsonify({"message": "Successfully sent friend request"}), 200
    else:
        return jsonify({"message": "Can't send friend request"}), 400


@main_app.route('/friends/request/<user_id>', methods=['PUT', 'DELETE'])
@token_required
@limit_request_frequency(num_requests=50, per_seconds=10)
@performance_logger
@functools.lru_cache(maxsize=128)
def accept_friends(current_user: current_user, user_id: str) -> jsonify:
    """
        Function handles the friends functionality which enables the user
        to accept friend requests and reject friend requests.
    """
    ID = current_user.ID
    user_data = update_redis_profile(ID)
    users_list = user_data.get
    friends_list = users_list.get("friend_requests")
    if request.method != 'PUT' and request.method != 'DELETE':
        abort(400, description='Invalid request')
    if friends_list is not None and user_id in friends_list:
        if request.method == 'PUT':
            update_redis_profile.accept_friend_requests(user_id, ID)
            user_data.update_friends(user_id)
            user_data.friend_request_remove(user_id)
            return jsonify({"message": "Friend request accepted"}), 200
        elif request.method == 'DELETE':
            if user_data.friend_request_remove(user_id):
                return jsonify({"message": "Friend request rejected"}), 200
    else:
        return jsonify({"message": "You have no friend requests"}), 400
