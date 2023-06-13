from .. import socketio
from flask_socketio import send, emit, join_room, leave_room
from models import redis_storage
from flask import request
from flask_login import current_user
import json


'''
    implementation of socketio server and client logic
'''

@socketio.on('connect')
def handle_connect():
    '''
        handle connect event
    '''
    print('\n\nclient connected to client\n\n')
    emit('connected', {'data': 'Connected'})

@socketio.on('message')
def handle_message(message):
    print('received message: ' + message)
    socketio.send(message)

@socketio.on('join')
def handle_join(data):
    '''
    handle join event
    '''
    username = current_user.User_name
    community = redis_storage.get_list_dict("community")
    if community:
        for idx, item in enumerate(community):
            for key, value in item.items():
                if username not in value['users'] and data == value['code']:
                    value['users'].append(username)
                    item[key] = value
                    redis_storage.update_list_dict("community", idx, item)
                    join_room(value['name'])
                    print("\n\nuser added to room\n\n")
                    emit('JoinRoom', {'room': value['name'], 'username': username}, room=value['name'])
                    return
        print("\n\ninvalid code or user already in room\n\n")
        emit('JoinRoom', {'message': 'error invalid code or user already in room'})
    else:
        print("\n\nno community\n\n")
        emit('JoinRoom', {'message': 'error no community'})

@socketio.on('disconnect')
def handle_disconnect():
    '''
        handle disconnect event
    '''
    print('\n\nclient disconnected from client\n\n')
