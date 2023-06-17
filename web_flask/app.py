#!/usr/bin/env python3
from web_flask import create_app, babel
import psutil
import os
import pstats
import click
import cProfile
from datetime import datetime
from werkzeug.serving import run_simple
from flask import request
from flask_socketio import SocketIO, emit, join_room, leave_room, send
from flask_login import current_user
from models import redis_storage

"""
    This is the entry point of the application.
    It creates the application instance and runs it.
"""

app = create_app('default')
socketio = SocketIO(app, async_mode='eventlet', cors_allowed_origins="*")
# migrate = Migrate(app, db)


@socketio.on('connect')
def test_connect():
    print('\n\nClient connected\n\n')
    emit('connected', {'data': 'Online'})


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
                    join_room(value['code'])
                    print("\n\nuser added to room\n\n")
                    emit('JoinRoom', {'room': value['name'], 'id': key, 'username': username}, room=value['code'])
                    return
                print("\n\ninvalid code or user already in room\n\n")
                emit('JoinRoom', {'message': 'error invalid code or user already in room'})
    else:
        print('\n\nno community\n\n')
        emit('JoinRoom', {'message': 'error no community'})

@socketio.on('send_message')
def handle_send_message(data):
    '''
        handle send message event
    '''
    username = current_user.User_name
    ID = current_user.id
    community = redis_storage.get_list_dict("community")
    message = data.get('message')
    room_id = data.get('id')
    print(f'\n\n{message} {room_id}\n\n')
    if community:
        for idx, item in enumerate(community):
            for key, value in item.items():
                if username in value['users'] and  str(room_id) == key:
                    print("yea made it here")
                    value['chat'].append({'text': message,
                                          'sender': username, 'date': datetime.now().strftime("%d/%m/%Y %H:%M:%S")})
                    item[key] = value
                    join_room(value['code'])
                    redis_storage.update_list_dict("community", idx, item)
                    data = {'message': message, 'username': username, 'id': ID, 'date': datetime.now().strftime("%d/%m/%Y %H:%M:%S")}
                    print(f"\n\n {data} \n\n")
                    emit('MsgFeedBack', data, room=value['code'])
                    return
    print("\n\nuser not in room\n\n")
    emit('MsgFeedBack', {'message': 'error user not in room'})


@socketio.on('leave')
def handle_leave(data):
    '''
        handle leave event
    '''
    username = current_user.User_name
    community = redis_storage.get_list_dict("community")
    if community:
        for idx, item in enumerate(community):
            for key, value in item.items():
                if username in value['users'] and data == value['code']:
                    value['users'].remove(username)
                    item[key] = value
                    redis_storage.update_list_dict("community", idx, item)
                    leave_room(value['code'])
                    print("\n\nuser removed from room\n\n")
                    emit('LeaveRoom', {'username': username}, room=value['code'])
                    return
                print("\n\ninvalid code or user not in room\n\n")
                emit('LeaveRoom', {'message': 'error invalid code or user not in room'})
    else:
        print('\n\nno community\n\n')
        emit('LeaveRoom', {'message': 'error no community'})

@socketio.on('disconnect')
def handle_disconnect():
    '''
        handle disconnect event
    '''
    print('\n\nclient disconnected from client\n\n')


"""
    babel.localeselector decorator registers the decorated function as a
    local selector function. The function is invoked for each request to
    select a language translation to use for that request.
    The function returns the best match language.
"""
@babel.localeselector
def get_locale():
    return request.accept_languages.best_match(app.config['LANGUAGES'])

@app.route('/test')
def make_shell_context():
    return dict(db=db)

"""
    The app.cli decorator registers a new command with the flask script.
    function runs a Source Code Profiling on the application and displays
    the result. The profiler measures the execution time of the functions
    in the application and the number of times each function was called.
    and saves the stats in a file.
"""
@app.cli.command()
@click.option('--length', default=25, help='Number of functions to include in the profiler report.')
@click.option('--profile-dir', default=None, help='Directory where profiler data files are saved.')
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
    print(f'Initial memory usage: {process.memory_info().rss / 1024 / 1024} MB')
    #app.run(port=5000, debug=False)
    socketio.run(app)
    #cProfile.run('main()', filename='myapp_profile.out')
    #app.server.serve_forever()
