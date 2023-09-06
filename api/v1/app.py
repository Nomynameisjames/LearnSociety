#!/usr/bin/python3
from flask import Flask, jsonify, make_response
from flask_cors import CORS
from werkzeug.exceptions import HTTPException
from dotenv import load_dotenv
from api.v1.main import main_app
import psutil
import os
import models

load_dotenv()
app = Flask(__name__)
#cache = Cache(app)
#app.config['CACHE_TYPE'] = 'redis'
#app.config['CACHE_REDIS_URL'] = 'redis://localhost:6379/0'
#swagger = Swagger(app)

app.url_map.strict_slashes = False
cors = CORS(app, resources={r"/api/v1/*": {"origin": "*"}})

app.register_blueprint(main_app)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')

host = os.getenv('HBNB_API_HOST', '127.0.0.1')
port = os.getenv('HBNB_API_PORT', '5000')


@app.teardown_appcontext
def teardown_db(e: Exception) -> None:
    models.storage.close()
    return


@app.errorhandler(400)
def handle_400(exception: HTTPException) -> dict:
    """
        handles 400 errros, in the event that global error handler fails
    """
    code = exception.__str__().split()[0]
    description = exception.description
    message = {'error': description}
    return make_response(jsonify(message), code)


@app.errorhandler(404)
def handle_404(exception: HTTPException) -> dict:
    """
        handles 404 errors, in the event that global error handler fails
    """
    code = exception.__str__().split()[0]
    description = exception.description
    message = {'error': description}
    return make_response(jsonify(message), code)


@app.errorhandler(Exception)
def global_error_handler(err: HTTPException) -> dict:
    """
        Global Route to handle All Error Status Codes
    """
    if isinstance(err, HTTPException):
        if type(err).__name__ == 'NotFound':
            err.description = "Not found"
        message = {'error': err.description}
        code = err.code
    else:
        message = {'error': err}
        code = 500
    return make_response(jsonify(message), code)


def setup_global_errors() -> None:
    """
        This updates HTTPException Class with custom error function
    """
    for cls in HTTPException.__subclasses__():
        app.register_error_handler(cls, global_error_handler)


if __name__ == '__main__':
    """
      MAIN Flask App
    """
    setup_global_errors()
    process = psutil.Process()
    print(
        f'Initial memory usage: {process.memory_info().rss / 1024 / 1024} MB')
    app.run(host=host, port=port)
