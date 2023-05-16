#!/usr/bin/python3

from api.v1.main import main_app
from flask import jsonify, request

@main_app.route('/status', methods=['GET'])
def status():
    if request.method == 'GET':
        resp = {"status": "OK"}
        return jsonify(resp)

