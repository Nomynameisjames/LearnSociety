#!/usr/bin/python3
from flask import render_template, flash, redirect, url_for
from flask_login import current_user, login_required
from typing import Any
from . import Main
from .form import SearchBar
from ..Performance_logger import performance_logger
from models.Schedule import Create_Schedule as Schedule
from models.Update_Profile import update_redis_profile


@Main.route('/help', methods=['GET', 'POST'])
@login_required
@performance_logger
def help() -> Any:
    """
        renders a template for the chatbot functionality
    """
    form = SearchBar()
    ID = current_user.ID
    uploader = update_redis_profile(ID)
    history = uploader.get
    chat_history = history.get("chat_bot")
    dp = history.get("profile_picture")
    if chat_history is None:
        chat_history = []
    if not ID:
        flash('Please login to access this page', 'danger')
        return redirect(url_for('Main.login'))
    return render_template('help.html', data=chat_history, form=form, dp=dp)


@Main.route('/settings', methods=['GET', 'PUT'])
@login_required
@performance_logger
def settings() -> Any:
    """
        renders a template for the settings page
    """
    ID = current_user.ID
    user_courses = Schedule(ID)
    target_list = []
    form = SearchBar()
    courses = ['Python', 'React', 'Javascript', 'C']
    for task in courses:
        target_list.append(user_courses.Target(task))
    return render_template('settings.html', form=form, target=target_list)
