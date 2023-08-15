#!/usr/bin/env python
from flask import render_template, flash
from flask_wtf.csrf import CSRFError
from . import Main

"""
   renders template for  Error handlers
    404: Page not found
    500: Internal server error
    401: Unauthorized
"""


@Main.app_errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@Main.app_errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500


@Main.app_errorhandler(401)
def server_error(e):
    return render_template('401.html'), 500


@Main.app_errorhandler(CSRFError)
def handle_csrf_error(e):
    flash('Missing CSRF token', 'error')
    return render_template('csrf_error.html', reason=e.description), 400
