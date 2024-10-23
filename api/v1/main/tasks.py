#!/usr/bin/python3
from flask import abort, jsonify, request
from flask_login import current_user
from datetime import datetime, timedelta
from typing import Dict, Tuple, Callable
from api.v1.main import main_app
from models.Schedule import Create_Schedule as cs
from models.Reminder import Reminder
from models import storage, redis_storage
from models.baseModel import (user_id, AutoSchedule, JSCourse,
                              ReactCourse, C_Course)
from functools import wraps, lru_cache
from models.RequestModule import SearchBar
import pprint
import jwt
import json
import re
import time


def token_required(f: Callable) -> Callable:
    @wraps(f)
    def decorated(*args, **kwargs) -> Tuple[Dict, int]:
        """
            decorator to check if user is logged in or not
            using a jwt token and validating based on secret key
        """
        from ..app import app
        token = None
        data = None
        if 'x-access-token' in request.headers:
            token = request.headers['x-access-token']
        if not token:
            return jsonify({'message': 'Token is missing!'}), 401
        try:
            data = jwt.decode(token, app.config['SECRET_KEY'],
                              algorithms=['HS256'])
            ID = data["user_id"]
            current_user = storage.access(ID, 'id', user_id)
        except Exception as e:
            return jsonify({"message": f"Token is invalid! {e}"}), 401
        return f(current_user, *args, **kwargs)
    return decorated


def limit_request_frequency(num_requests=1, per_seconds=1):
    """
        Limits the frequency of requests made by a user.
        :param num_requests: maximum number of requests that can be made in
        the given time period :param per_seconds: time period in seconds
    """
    def decorator(func: Callable) -> Callable:
        last_request_times = {}

        @wraps(func)
        def wrapper(*args, **kwargs) -> Callable:
            ip_address = request.remote_addr
            if ip_address not in last_request_times:
                last_request_times[ip_address] = [time.time()]
            else:
                elapsed_time = time.time() - last_request_times[ip_address][-1]
                if elapsed_time < per_seconds:
                    if len(last_request_times[ip_address]) >= num_requests:
                        abort(429)
                else:
                    last_request_times[ip_address].append(time.time())
            return func(*args, **kwargs)
        return wrapper
    return decorator


@main_app.route('/tasks', methods=['GET', 'POST'])
@token_required
@limit_request_frequency(num_requests=20, per_seconds=60)
def task(current_user: current_user) -> jsonify:
    """
        GET: Retrieves all self customised tasks for a user
        POST: Creates a new task for a user
    """
    ID = current_user.ID
    bot = cs(ID)
    if request.method == 'POST':
        req_json = request.get_json()
        required_fields = ['Day', 'Course', 'Topic', 'Reminder']
        missing_fields = [field for field in required_fields if not
                          req_json.get(field)]
        if missing_fields:
            abort(400, f'Missing fields: {", ".join(missing_fields)}')
        bot.Create(**req_json)
        bot.Save()
        return jsonify(bot.View()), 200


@main_app.route('/tasks/<int:my_id>', methods=['GET', 'PUT', 'DELETE'])
@token_required
@limit_request_frequency(num_requests=20, per_seconds=60)
def get_task(current_user: current_user, my_id: int) -> jsonify:
    """
        GET: Retrieves a single self customised task for a user
        PUT: Updates a single task for a user
        DELETE: Deletes a single task for a user
    """
    ID = current_user.ID
    data = storage.access(ID, 'id', user_id)
    file = storage.view(ID)[1]
    Tasks = None
    if data:
        Tasks = data.schedules
    if request.method == 'GET':
        for key, value in file.items():
            if key == my_id:
                data = value
                return jsonify(data), 200
            elif key != my_id:
                return jsonify({"message": "ID not in list"}), 404

    if request.method == 'PUT':
        req_json = request.get_json()
        if req_json is None:
            abort(400, 'Not JSON')
        updated_dict = {}
        for key, value in req_json.items():
            if Tasks:
                for index, task in enumerate(Tasks):
                    if task.ID == my_id:
                        if hasattr(task, key):
                            setattr(Tasks[index], key, value)
                        updated_dict[key] = value
                        Tasks[index].Updated_at = datetime.now()
        if not updated_dict:
            abort(400, "No valid keys found")
        storage.save()
        return jsonify(updated_dict), 200

    if request.method == 'DELETE':
        obj = None
        if Tasks:
            for item in Tasks:
                if item.ID == my_id:
                    obj = item
        if obj is None:
            abort(404, 'ID not in list')
        storage.delete(obj)
        del obj
        storage.save()
        return jsonify({"message": "data removed"}), 200


@main_app.route('/reminder', methods=['POST'])
@token_required
@limit_request_frequency(num_requests=20, per_seconds=60)
def reminder(current_user: current_user) -> jsonify:
    """
        POST: Sends a reminder to a user by making a request to the twillio
        API
    """
    ID = current_user.ID
    if request.method == 'POST':
        bot = Reminder(ID)
        req_json = request.get_json()
        if req_json is None:
            abort(400, 'Not JSON')
        bot.Twilio(**req_json)
        return jsonify({"Success": "Reminder sent"}), 200


@main_app.route('/auto-dash', methods=['POST'])
@token_required
@limit_request_frequency(num_requests=20, per_seconds=60)
def auto_dash(current_user: current_user) -> jsonify:
    """
        POST: Registers a new course for a user by retriving courses
        saved in the specified json file and creating a schedule
    """
    ID = current_user.ID
    data = storage.access(ID, 'id', user_id)
    files = None
    if data:
        files = {
            "Python": [
                AutoSchedule, data.auto_schedules, 'Python_Courses.json'
                ],
            "Javascript": [JSCourse, data.JScourse, 'JSCourse.json'],
            "React": [ReactCourse, data.Reactcourse, 'React_Courses.json'],
            "C": [C_Course, data.C_course, 'C_courses.json']
            }
    req_json = request.get_json()
    course = req_json.get('Course')
    doc = None
    key = None
    if files and course in files:
        doc = files.get(course)
    if doc:
        key = [i for i in doc[1] if i.user_ID == ID]
    now = datetime.utcnow().date()
    if request.method == 'POST':
        day = req_json.get("Day")
        day = datetime.strptime(day, "%Y-%m-%d").date()
        if day < now:
            return jsonify({"message": "Date is in the past"}), 400
        if key:
            return jsonify({"message": "User task already set"}), 400
        if doc:
            try:
                with open(doc[2], 'r') as f:
                    courses = json.load(f)
                    file = [v for v in courses.values()]
                    for i, topic in enumerate(file):
                        date = day + timedelta(days=i)
                        task = doc[0](user_ID=ID,
                                    Days=date,
                                    Course=topic["Course"],
                                    Topic=topic["Topic"],
                                    Target=False,
                                    Reminder=req_json.get("Reminder"),
                                    Created_at=datetime.utcnow().date())
                        storage.new(task)
                storage.save()
                return jsonify({"message": f"{course} created"}), 200
            except FileNotFoundError:
                return jsonify({"message": "Course not found"}), 400


@main_app.route('/wikisearch', methods=['POST'])
@token_required
@lru_cache(maxsize=128)
@limit_request_frequency(num_requests=20, per_seconds=60)
def searchBar(*args, **kwargs) -> jsonify:
    """
        function creates an instance of the SearchBar class and calls the
        Wikipedia method to search for a topic if not found makes a call to the
        get_wiki method to search for the topic and caches the results in
        Redis
    """
    req_json = request.get_json()
    data = req_json.get('text')
    temp_dict = {}
    search_Func = SearchBar()
    doc = None
    if request.method == 'POST':
        try:

            dictionary = redis_storage.get_list_dict("dictionary")
            pattern = re.compile(fr"\b{data}\b", re.IGNORECASE)
            # Search the Redis dictionary first
            if dictionary:
                for item in dictionary:
                    for key, value in item.items():
                        if pattern.search(key):
                            return jsonify(value), 200
            # Otherwise, use Wikipedia module
            else:
                doc = search_Func.Wikipedia(data)
                if doc:
                    temp_dict[data] = doc
                    dictionary.append(temp_dict)
                    redis_storage.set_list_dict('dictionary', dictionary)
                    return jsonify(doc), 200
            # If there's still no response, use get_wiki_briefs module
        except Exception as e:
            print(e)
        if doc is None:
            doc = search_Func.google_search(data)
            if doc and isinstance(doc, list):
                dictionary = redis_storage.get_list_dict("dictionary")
                #doc = doc[0]
                #doc = ' '.join(doc)
                temp_dict[data] = doc[0]
                dictionary.append(temp_dict)
                redis_storage.set_list_dict('dictionary', dictionary)
                return jsonify(doc[0]), 200
            return jsonify({"description": "No results found"}), 404


@main_app.route('/search/<topic>', methods=['POST'])
@token_required
@limit_request_frequency(num_requests=20, per_seconds=60)
@lru_cache(maxsize=128)
def Subject_search(*args, topic: str) -> jsonify:
    """
        function creates an instance of the SearchBar class and calls the
        get_recommendations method to search for a topic and retrive the link
        to the resources this is then passed to the get_resource method to
        webscrap the resource and cache the results in Redis
    """
    req_json = request.get_json()
    data = req_json.get('text')
    temp_dict = {}
    search_Func = SearchBar()
    doc = None
    if request.method == 'POST':
        if topic == "Python":
            try:
                dictionary = redis_storage.get_list_dict("PythonFiles")
                pattern = re.compile(fr"\b{data}\b", re.IGNORECASE)
                # Search the Redis dictionary first
                if dictionary:
                    for item in dictionary:
                        for key, value in item.items():
                            if pattern.search(key):
                                return jsonify({"Document": value}), 200
                web_scrap = search_Func.get_recommendations(data)
                Scrapped = []
                if isinstance(web_scrap, list):
                    Scrapped = web_scrap
                doc = search_Func.get_resource(Scrapped, data)
                if doc:
                    temp_dict[data] = doc
                    dictionary.append(temp_dict)
                    redis_storage.set_list_dict('PythonFiles', dictionary)
                    return jsonify({"Document": doc}), 200
                else:
                    return jsonify({"description": "No results found"}), 404
            except Exception as e:
                print(f'\n {e} \n')
                return jsonify({"description": """Error occurred while
                                                searching"""}), 500
