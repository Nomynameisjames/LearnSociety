#!/usr/bin/python3
from flask import render_template, flash, redirect, url_for
from . import Main 
from .form import SearchBar
from models.Schedule import Create_Schedule as Schedule
from flask_login import current_user, login_required
from ..Performance_logger import performance_logger
import models

"""
     renders  a template for the chatbot functionality
"""
@Main.route('/help', methods=['GET', 'POST'])
@login_required
@performance_logger
def help():
    form = SearchBar()
    ID = current_user.id
    user = current_user.User_name
    cache_key = f"conv_ID_{ID}"
    history = models.redis_storage.get_list(cache_key)
    if not ID:
        flash('Please login to access this page', 'danger')
        return redirect(url_for('Main.login'))
    return render_template('help.html', user=user, data=history, form=form,
                           ID=ID) 

@Main.route('/settings', methods=['GET', 'PUT'])
@login_required
@performance_logger
def settings():
    """
        renders a template for the settings page
    """
    ID = current_user.id
    user_courses = Schedule(ID)
    target_list = []
    form = SearchBar()
    courses = ['Python', 'React', 'Javascript', 'C']
    dic = {'user': current_user.User_name,
           'Email': current_user.Email,
           'phone': current_user.Phone_number,
           'ID': ID,
           'auto': current_user.save_history
        }
    for task in courses:
        target_list.append(user_courses.Target(ID, task)[0])
    if form.validate_on_submit():
       ''' usr = models.storage.access(ID, 'id', user_id)
        if usr and check_password_hash(usr.Password, form.old_password.data):
            hash_password = generate_password_hash(form.password.data)
            user.Password = hash_password
            models.storage.save()
            models.storage.close()
            flash('Password successfully changed', 'success')
            if request.is_xhr:
                return jsonify({'message': 'Password successfully changed'})
        else:
            if request.is_xhr:
                return jsonify({'message': 'Password not changed, please try again'})
        #if not ID:
         #   flash('Please login to access this page', 'danger')
          #  return redirect(url_for('Main.login'))
    elif request.method == 'GET': '''
    return render_template('settings.html', data=dic,
                           form=form, target=target_list)
