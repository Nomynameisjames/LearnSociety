#!/usr/bin/python3
from api.v1.main import main_app
from flask import abort, jsonify, request
from models.Schedule import Create_Schedule as cs
from models import redis_storage
from models.checker import Checker
from models.Update_Profile import update_redis_profile
from .tasks import token_required, limit_request_frequency
from web_flask.Performance_logger import performance_logger
from .update_data import Settings, create_community
import yaml

obj = {} # temp storage for quiz data
quiz_answers = {} # temp storage for quiz answers

'''
    enables the chat bot functionality by creating an instance of the checker
    class and calling the help method to process the user's request to the
    openAI api 
'''
@main_app.route('/help', methods=['GET', 'POST'])
@token_required
@limit_request_frequency(num_requests=3, per_seconds=10)
@performance_logger
def help(current_user):
    ID = current_user.id
    bot = Checker(ID)
    uploader = update_redis_profile(ID)
    req_data = request.get_json()
    if request.method == 'POST':
        for text in req_data.values():
            data = bot.Help(text)
            message = {text: data}
            return jsonify(message), 200
    if request.method == 'DELETE':
        uploader.clear_chatbot_history()
        return jsonify({"message": "successfully removed"}), 200
    else:
        abort(400, description='Failed to perform request')
    

'''
    function handles the quiz functionality which gets the quiz answers from the
    user and sends them to the openAI api for processing using the checker class
    static method _invoke_chatbot, validate and updates the users average
    score in the mysql database using the static method check_answers
'''
@main_app.route('/quiz', methods=['GET', 'POST'])
@token_required
@limit_request_frequency(num_requests=3, per_seconds=10)
@performance_logger
def quiz(current_user):
    ID = current_user.id
    quiz_answers = request.get_json()
    Key = None
    Value = {}
    for k, v in quiz_answers.items():
        Key = k
        Value = v
    if Key is None:
        abort(404, description='Core credentials not found')
    
    new_key = list(Value.keys())
    new_key = ''.join(new_key).split('.')
    new_key.pop(0)
    if request.method == 'POST':
        if quiz_answers is None:
            abort(404, description='invalid request')
        else:
            if not obj:
                for _, values in Value.items():
                    obj[Key] = dict(zip(new_key, values))
                data = Checker._invoke_chatbot(obj)
                if Key:
                    Checker.check_answers(data, ID, int(Key))
                message = {Key: data}
                with open('tasks.yaml', 'a') as f:
                    yaml.dump(message, f)
                return jsonify(message), 201
            else:
                return jsonify({"message": "Quiz data already present"}), 204
    if request.method == 'GET':
        with open('tasks.yaml', 'r') as f:
            file = yaml.safe_load(f)
        if file is None:
            abort(404, description='Resource not found')
        else:
            return jsonify(file), 200


@main_app.route('/settings/', methods=['POST', 'DELETE'])
@token_required
@limit_request_frequency(num_requests=3, per_seconds=10)
@performance_logger
def settings(current_user):
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
        if data is None:
            abort(404, 'invalid credentials')
        else:
            if option not in options:
                abort(404, 'invalid request')
            else:
                function = options[option]
                Request_obj =  function()
                if Request_obj:
                    return jsonify({"message": Request_obj}), 200


    if request.method == 'DELETE':
        if data is None:
            abort(404, description='record not found')
        else:
            if option not in options:
                abort(404, description='invalid request')
            else:
                function = options[option]
                Request_obj =  function()
                if Request_obj:
                    return jsonify({"message": Request_obj}), 200
    else:
        abort(400, description='invalid request')


@main_app.route('/settings/', methods=['PUT'])
@token_required
@limit_request_frequency(num_requests=3, per_seconds=60)
@performance_logger
def Update_user_profile(current_user):
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
        'password': update_func.update_password
    }

    if request.method == 'PUT':
        if data is None:
            abort(404, 'invalid credentials')
        else:
            if option not in options:
                abort(404, 'invalid request')
            else:
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
def community(current_user):
    """
        function handles the community functionality which enables the user
        to create a room
    """
    ID = current_user.id
    username = current_user.User_name
    data = request.get_json()
    room = data.get('room')
    description = data.get('description')
    #if current_user.Rooms:
    #    return jsonify({"message": "You already have a room"}), 200
    new_room = {
            'name': room,
            'description': description,
            'admin': username
            }
    Community = create_community(ID, **new_room)
    if Community:
        return jsonify({"message": "successfully created"}), 201
    else:
        return jsonify({"message": "Can't create room"}), 400

@main_app.route('/community/', methods=['PUT', 'DELETE'])
@token_required
@limit_request_frequency(num_requests=3, per_seconds=10)
@performance_logger
def Update_community(current_user):
    """
        function handles the community functionality which enables the admin user
        to clear a room chat history
    """
    username = current_user.User_name
    data = request.get_json()
    room_code = data.get('room_code')
    edit_description = data.get('description')
    new_room_name = data.get('new_name')
    community = redis_storage.get_list_dict("community")
    if community:
        for idx, item in enumerate(community):
            for key, value in item.items():
                if value.get("code") == room_code.strip() and value.get("admin") == username.strip():
                    print("inside condition code active")
                    if request.method == 'PUT':
                        print("inside put request")
                        value["description"] = edit_description
                        value["name"] = new_room_name
                        item[key] = value
                        redis_storage.update_list_dict("community", idx, item)
                        return jsonify({"message": "successfully updated room info"}), 200
                    elif request.method == 'DELETE':
                        print("inside delete request")
                        value.get("chat").clear()
                        item[key] = value
                        redis_storage.update_list_dict("community", idx, item)
                        return jsonify({"message": "successfully deleted"}), 200
                    else:
                        print("inside else request")
                        abort(400, description='invalid request')
                else:
                    print("inside else request invalid permission")
                    return jsonify({"description": "you don't have admin privileges to modify room data"}), 400
        return jsonify({"description": "some error occured"}), 400
