'''
    implementatino of socketio server and client logic
'''
#from flask_socketio import send, emit
#from .. import socketio
#from models import redis_storage

#@socketio.on('connect')
def handle_connect():
    '''
        handle connect event
    '''
    print('client connected')

