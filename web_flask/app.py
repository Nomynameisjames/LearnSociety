#!/usr/bin/env python3
import psutil
import os
import pstats
import click
import cProfile
from datetime import datetime
from flask import request
from flask_socketio import SocketIO, emit, join_room, leave_room
from flask_login import current_user
from sortedcontainers import SortedList
from web_flask import create_app, babel
#from models import redis_storage
from models.Update_Profile import update_redis_profile
from models.community_data import CommunityData

"""
    This is the entry point of the application.
    It creates the application instance and runs it.
"""

app = create_app('default')
socketio = SocketIO(app, async_mode='eventlet', cors_allowed_origins="*")


@socketio.on('connect')
def Groupconnect() -> None:
    """
        connect to socket
    """
    emit('connected', {'data': 'Online'})


@socketio.on('message')
def handle_message(message) -> None:
    """
        no practical use case for this event, just testing the send method
    """
    socketio.send(message)


@socketio.on('join')
def handle_join(data: str) -> None:
    '''
        join event enables a user join a community, takes the community
        code as parameter and checks if the user is already in the community
        if not, the user is added to the community and the user is added to the
        room with the community code
    '''
    username = current_user.User_name
    community = CommunityData()
    find_community = community.join_community(username, data)
    if find_community:
        room_code = find_community.get('code')
        join_room(room_code)
        emit('JoinRoom', find_community, room=room_code)
    else:
        emit('JoinRoom',
             {'message': 'error invalid code or user already in room'})


@socketio.on('send_message')
def handle_send_message(data: dict) -> None:
    '''
        send message event, takes the message and the room code as parameter
        and saves the message to the community chat history in the redis
        database and emits the message to the specified room
    '''
    username = current_user.User_name
    ID = current_user.ID
    community = CommunityData()
    sender_data = update_redis_profile(ID)
    message = data.get('message')
    room_id = data.get('id')
    current_datetime = datetime.now()
    payload = {
                "sender_id": ID,
                "text": str(message),
                "name": username,
                "time": current_datetime.strftime("%-d %b %Y %I:%M:%S%p"),
                "profile_pic": sender_data.value["profile_picture"]
            }
    save_chat = community.update_chat_history(username, room_id, **payload)
    if save_chat:
        join_room(save_chat)
        emit('MsgFeedBack', payload, room=save_chat)
    else:
        emit('MsgFeedBack', {'message': 'error user not in room'})


@socketio.on('leave')
def handle_leave(data: str) -> None:
    '''
        handle leave event takes the room code as parameter and removes the
        user from the room and emits the leave event to the room
    '''
    username = current_user.User_name
    community = CommunityData()
    value = community.leave_community(username, data)
    if value:
        leave_room(value)
        emit('LeaveRoom', {'username': username}, room=value)
    else:
        emit('LeaveRoom',
             {'message': 'error invalid code or user not in room'})


@socketio.on('disconnect')
def handle_disconnect():
    '''
        handle disconnect event
    '''
    print('\n\nclient disconnected from client\n\n')


@socketio.on('connect', namespace='/private')
def Privateconnect():
    try:
        user_id = current_user.ID
        user = update_redis_profile(user_id)
        ID = request.sid
        friends_list = []
        if user.update_online_id(ID):
            friends_list = user.view_online_friends()
        print(f"{type(friends_list)}\n {friends_list}")
        emit('Private_connection', {"data": friends_list})
    except Exception as e:
        print(e)

@socketio.on('Private_message', namespace='/private')
def PrivateMessage(data):
    try:
        user_id = current_user.ID
        recipient_id = data['recipient_id']
        payload = {}
        message = data['message']
        reciepient_data = update_redis_profile(recipient_id)
        sender_data = update_redis_profile(user_id)
        sorted_ids = SortedList([user_id, recipient_id])
        room_name = '-'.join(str(id) for id in sorted_ids)
        join_room(room_name)
        current_datetime = datetime.now()
        payload = {
            "sender_id": user_id,
            "text": str(message),
            "name": current_user.User_name,
            "time": current_datetime.strftime("%-d %b %Y %I:%M:%S%p"),
            "profile_pic": sender_data.value["profile_picture"]
        }
        emit('Private_message', payload, room=room_name)
        payload.pop("sender_id", None)
        payload.pop("profile_pic", None)
        reciepient_data.save_userchat_history(user_id, **payload)
        sender_data.save_userchat_history(recipient_id, **payload)
    except Exception as e:
        print(e)


@socketio.on('disconnect', namespace='/private')
def PrivateDisconnect():
    try:
        user_id = current_user.ID
        user = update_redis_profile(user_id)
        for item in user.data:
            for user_id in item.keys():
                if user.update_online_id(''):
                    emit('Private_connection', "Offline")
    except Exception as e:
        print(e)
        emit('Private_connection', "error")


"""
    babel.localeselector decorator registers the decorated function as a
    local selector function. The function is invoked for each request to
    select a language translation to use for that request.
    The function returns the best match language.
"""


#@babel.localeselector
#def get_locale():
#    return request.accept_languages.best_match(#app.config['LANGUAGES'])


"""
    The app.cli decorator registers a new command with the flask script.
    function runs a Source Code Profiling on the application and displays
    the result. The profiler measures the execution time of the functions
    in the application and the number of times each function was called.
    and saves the stats in a file.
"""


@app.cli.command()
@click.option('--length', default=25,
              help='Number of functions to include in the profiler report.')
@click.option('--profile-dir', default=None,
              help='Directory where profiler data files are saved.')
def profile(length, profile_dir):
    """Start the application under the code profiler."""
    profiler = cProfile.Profile()
    profiler.enable()

    profiler.disable()
    stats = pstats.Stats(profiler)
    stats.strip_dirs()
    stats.sort_stats('cumulative')
    stats.print_stats(length)
    if profile_dir:
        stats.dump_stats(os.path.join(profile_dir, 'myapp_profile.out'))


if __name__ == '__main__':
    process = psutil.Process()
    print(
        f'Initial memory usage: {process.memory_info().rss / 1024 / 1024} MB')
    socketio.run(app)
