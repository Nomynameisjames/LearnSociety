from flask import Flask
#from flask_socketio import SocketIO
from flask_bootstrap import Bootstrap
from flask_mail import Mail
from flask_moment import Moment
from flask_login import LoginManager
from flask_jwt_extended import JWTManager
from flask_wtf.csrf import CSRFProtect
from web_flask.config import config
from flask_cors import CORS
from flask_caching import Cache
from flask_babel import Babel
from flask_babel import lazy_gettext as _l
from datetime import timedelta
#from flask_socketio import SocketIO
import models 
#import eventlet
#eventlet.monkey_patch()


bootstrap = Bootstrap()
mail = Mail()
moment = Moment()
jwt = JWTManager()
csrf = CSRFProtect()
login_manager = LoginManager()
babel = Babel()
#socketio = SocketIO()
cors = CORS()
#cache = Cache(config={'CACHE_TYPE': 'SimpleCache',
#                      "CACHE_DEFAULT_TIMEOUT": 300})

def create_app(config_name):
    """
        Create an application instance using the specified configuration.
        :param config_name: name of the configuration to use
        :return: the application instance
    """
    from .main import Main as main_blueprint
    app = Flask(__name__)
    app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=60)
    #app.config['FLASK_SOCKETIO_ASYNC_MODE'] = 'eventlet'
    #app.config['SERVER_NAME'] = 'localhost.localdomain:5000'
    app.register_blueprint(main_blueprint)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)
    bootstrap.init_app(app)
    cors.init_app(app)
    #socketio.init_app(app, cors_allowed_origins="*", async_mode='eventlet')
#    cache.init_app(app)
    jwt.init_app(app)
    babel.init_app(app)
    csrf.init_app(app)
    mail.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'Main.login'
    login_manager.login_message_category = 'info'
    login_manager.login_message = _l('Please log in to access this page.')
    moment.init_app(app)
    mail.init_app(app)
    #socketio.init_app(app, cors_allowed_origins="*")
    return app
