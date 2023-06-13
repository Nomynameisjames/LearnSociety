from flask import Blueprint

"""
    Blueprint is a way to organize a group of related views and other code.
    Rather than registering views and other code directly with an application,
    they are registered with a blueprint. Then the blueprint is registered
    with the application when it is available in the factory function.
"""
Main = Blueprint('Main', __name__) 

from . import views, errors, auth, Help, socket
