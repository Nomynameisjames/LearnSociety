#!/usr/bin/python3
from api.v1.main import main_app
from flask import abort, jsonify, request
from models.Schedule import Create_Schedule as cs
from models.Reminder import Reminder
from models import storage, redis_storage
from datetime import datetime, timedelta
from flask_login import current_user, login_required
from models.baseModel import (User, user_id, AutoSchedule, JSCourse,
                                ReactCourse, C_Course)
from functools import wraps
from models.RequestModule import SearchBar
import jwt
import json
import re
import time

"""
   decorator to check if user is logged in or not
   using a jwt token and validating based on secret key
"""
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        from ..app import app
        token = None
        data = None
        if 'x-access-token' in request.headers:
            token = request.headers['x-access-token']
        if not token:
            return jsonify({'message' : 'Token is missing!'}), 401
        try:
            data = jwt.decode(token, app.config['SECRET_KEY'],
                              algorithms=['HS256'])
            ID = data["user_id"]
            current_user = storage.access(ID, 'id', user_id)
        except:
            return jsonify({"message" : "Token is invalid!"}), 401
        return f(current_user, *args, **kwargs)
    return decorated


def limit_request_frequency(num_requests=1, per_seconds=1):
    """
    Limits the frequency of requests made by a user.
    :param num_requests: maximum number of requests that can be made in the given time period
    :param per_seconds: time period in seconds
    """
    def decorator(func):
        last_request_times = {}
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Get the IP address of the user making the request
            ip_address = request.remote_addr

            # If this is the first request from the user, then create a new entry in the dictionary
            if ip_address not in last_request_times:
                last_request_times[ip_address] = [time.time()]

            # Otherwise, check if the time between this request and the last request is less than per_seconds
            else:
                elapsed_time = time.time() - last_request_times[ip_address][-1]
                if elapsed_time < per_seconds:
                    # If the user has already made num_requests within the given time period, then abort the request
                    if len(last_request_times[ip_address]) >= num_requests:
                        abort(429)
                else:
                    last_request_times[ip_address].append(time.time())

            # Call the original function and return the response
            return func(*args, **kwargs)

        return wrapper

    return decorator

@main_app.route('/tasks', methods=['GET', 'POST'])
@token_required
@limit_request_frequency(num_requests=3, per_seconds=10)
def task(current_user):
    """
        GET: Retrieves all self customised tasks for a user
        POST: Creates a new task for a user
    """
    ID = current_user.id
    username = current_user.User_name
    bot = cs(ID)
    if request.method == 'GET':
        doc = storage.view(ID)[1]
        return jsonify(doc), 200

    if request.method == 'POST':
        req_json = request.get_json()
        required_fields = ['Day', 'Course', 'Topic', 'Reminder']
        missing_fields = [field for field in required_fields if not
                          req_json.get(field)]
        if missing_fields:
            abort(400, f'Missing fields: {", ".join(missing_fields)}')
        bot.Create(**req_json)
        bot.Save()
        cache_key = f'user_{ID}_{username}'
        redis_storage.delete(cache_key)
        return jsonify(bot.View(ID)), 200


@main_app.route('/tasks/<int:my_id>', methods=['GET', 'PUT', 'DELETE'])
@token_required
@limit_request_frequency(num_requests=3, per_seconds=10)
def get_task(current_user, my_id):
    """
        GET: Retrieves a single self customised task for a user
        PUT: Updates a single task for a user
        DELETE: Deletes a single task for a user
    """
    ID = current_user.id
    username = current_user.User_name
    cache_key = f'user_{ID}_{username}'
    data = storage.view(ID)[0].get(ID)
    file = storage.view(ID)[1]
    doc = None
    if data:
        doc = data.schedules
    if request.method == 'GET':
        for key, value in file.items():
            if key == my_id:
                data = value
                return jsonify(data), 200
            elif key != my_id:
                return jsonify({"message" : "ID not in list"}), 404

    if request.method == 'PUT':
        req_json = request.get_json()
        if req_json is None:
            abort(400, 'Not JSON')
        updated_dict = {}
        for key, value in req_json.items():
            if doc:
                for index, task in enumerate(doc):
                    if task.id == my_id:
                        if hasattr(task, key):
                            setattr(doc[index], key, value)
                        updated_dict[key] = value
                        doc[index].Updated_at = datetime.now()
        if not updated_dict:
            abort(400, "No valid keys found")
        storage.save()
        redis_storage.delete(cache_key)
        return jsonify(updated_dict), 200

    if request.method == 'DELETE':
        obj = None
        if doc:
            for item in doc:
                if item.id == my_id:
                    obj = item
        if obj is None:
            abort(404, 'ID not in list')
        storage.delete(obj) 
        del obj
        storage.save()
        redis_storage.delete(cache_key)
        return jsonify({"Success" : "data removed"}), 200



@main_app.route('/reminder', methods=['POST'])
@token_required
@limit_request_frequency(num_requests=3, per_seconds=10)
def reminder(current_user):
    """
        POST: Sends a reminder to a user by making a request to the twillio
        API
    """
    ID = current_user.id
    if request.method == 'POST':
        bot = Reminder(ID)
        req_json = request.get_json()
        bot.Twilio(**req_json)
        return jsonify({"Success" : "Reminder sent"}), 200

@main_app.route('/auto-dash', methods=['POST'])
@token_required
@limit_request_frequency(num_requests=3, per_seconds=10)
def auto_dash(current_user):
    """
        POST: Creates a new auto schedule for a user by retriving courses
        saved in the specified json file and creating a schedule for the user
    """
    ID = current_user.id
    data = storage.view(ID)[0].get(ID)
    files = None
    if data:
        files = {
            "Python" : [AutoSchedule, data.auto_schedules, 'Python_Courses.json'],
            "Javascript" : [JSCourse, data.JScourse, 'JSCourse.json'],
            "React" : [ReactCourse, data.Reactcourse, 'React_Courses.json'],
            "C" : [C_Course, data.C_course, 'C_courses.json']
            }
    req_json = request.get_json()
    course = req_json.get('Course')
    doc = None
    key = None
    if course in files:
        if files:
            doc = files.get(course)
    if doc:
        key = [i for i in doc[1] if i.user_ID == ID]
    now = datetime.utcnow().date()

    if request.method == 'POST':
        day = req_json.get("Day")
        day = datetime.strptime(day, "%Y-%m-%d").date()
 
         # Check if the specified date is in the past
        if day < now:
            return jsonify({"message": "Date is in the past"}), 400
 
 # Check if the user already has a task set for this day
        if key:
            return jsonify({"message": "User task already set"}), 400
 
         # Create a new schedule for the user
        if doc: 
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
                                    Created_at=now)
                    storage.new(task)
            storage.save()
            return jsonify({"Success": "Auto dash set"}), 200
        else:
            return jsonify({"message": "Course not found"}), 400
 
@main_app.route('/search', methods=['POST'])
@token_required
@limit_request_frequency(num_requests=3, per_seconds=10)
def searchBar(current_user):
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

            dictionary = redis_storage.get_list("dictionary")
            pattern = re.compile(fr"\b{data}\b", re.IGNORECASE)
            # Search the Redis dictionary first
            if dictionary:
                print("using the redis module")
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
                    redis_storage.set_dict('dictionary', dictionary)
                    print("using the wikipedia module")
                    return jsonify(doc), 200
            
            # If there's still no response, use get_wiki_briefs module
        except:
            pass
        if doc is None:
            doc = search_Func.get_wiki_briefs(data)
            if doc:
                dictionary = redis_storage.get_list("dictionary")
                print("using the get_wiki module")
                doc = doc.get('summary')
                doc = ' '.join(doc)
                temp_dict[data] = doc
                dictionary.append(temp_dict)
                redis_storage.set_dict('dictionary', dictionary)
                return jsonify(doc), 200
        return jsonify({"description" : "No results found"}), 404
        
        #except:
        #    return jsonify({"description" : "Error occurred while searching"}), 500

@main_app.route('/search/<topic>', methods=['POST'])
@token_required
@limit_request_frequency(num_requests=3, per_seconds=10)
def Subject_search(current_user, topic):
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
                dictionary = redis_storage.get_list("PythonFiles")
                pattern = re.compile(fr"\b{data}\b", re.IGNORECASE)
                # Search the Redis dictionary first
                if dictionary:
                    print("using the redis module")
                    for item in dictionary:
                        for key, value in item.items():
                            if pattern.search(key):
                                return jsonify({"Document": value}), 200
            
                web_scrap = search_Func.get_recommendations(data)
                doc = search_Func.get_resource(web_scrap)
                if doc:
                    temp_dict[data] = doc
                    dictionary.append(temp_dict)
                    redis_storage.set_dict('PythonFiles', dictionary)
                    print("using the web_scrap module")
                    return jsonify({"Document": doc}), 200
                else:
                    return jsonify({"description" : "No results found"}), 404
            except:
                return jsonify({"description" : f"""Error occurred while
                                                searching"""}), 500
