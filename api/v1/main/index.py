#!/usr/bin/python3
from api.v1.main import main_app
from flask import jsonify, request


@main_app.route('/status', methods=['GET'])
def status() -> jsonify:
    """
        Return status of the API
    """
    if request.method == 'GET':
        return jsonify({"status": "OK"})
