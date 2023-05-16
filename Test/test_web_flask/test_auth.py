#!/usr/bin/env python3
"""
    import files
"""
import unittest
import models
import re
import os
import uuid
import web_flask
from web_flask.app import app
from flask_testing import TestCase
from web_flask.main.auth import new_user_token
from flask import url_for
from werkzeug.security import generate_password_hash
from werkzeug.datastructures import MultiDict
from werkzeug.test import EnvironBuilder
from unittest.mock import patch
from unittest import mock
from models.RequestModule import Notifications
from models.baseModel import user_id

class TestAuth(TestCase):
    obj = Notifications()
    def setUp(self):
        self.user = None
        self.user_id = str(uuid.uuid4())
        self.user_token = new_user_token(self.user_id)
        self.app_context = self.app.app_context()
        self.app_context.push()
        self.client = self.app.test_client()
        self.user_data = {
            'Username': 'test_user',
            'Email': 'test_email@example.com',
            'Password': 'test_password',
            'id': self.user_id
        }
        models.redis_storage.set_dict(self.user_id, [self.user_data], ex=100)

    def tearDown(self):
        models.redis_storage.delete(self.user_id)
        models.storage.delete(self.user)
        models.storage.close()
        self.app_context.pop()

    def create_app(self):
        app.config['WTF_CSRF_ENABLED'] = True
        app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
        return app


    def get_csrf_token(self, response_data):
        pattern = re.compile(r'<input[^>]*name="csrf_token"[^>]*value="([^"]+)"')
        match = pattern.search(response_data.decode())
        if match:
            return match.group(1)
        else:
            return None

    @patch('web_flask.main.auth.verify_new_user_token')
    def test_confirm_email_success(self, mock_verify_new_user_token):
        mock_verify_new_user_token.return_value = self.user_data
        response = self.client.get(f'/confirm_email/{self.user_id}/{self.user_token}')
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.location, f'/login')
        response = self.client.get(response.location)
        self.assertIn(b'Account created successfully for test_user', response.data)
        self.user = models.storage.access(self.user_id, 'id', user_id)
        self.assertIsInstance(self.user, user_id)
        self.assertEqual(self.user.User_name, self.user_data['Username'])
        self.assertEqual(self.user.Email, self.user_data['Email'])
        self.assertEqual(self.user.Password, self.user_data['Password'])
    
    @patch('web_flask.main.auth.verify_new_user_token')
    def test_confirm_email_fail(self, mock_verify_new_user_token):
        mock_verify_new_user_token.return_value = None
        response = self.client.get(f'/confirm_email/{self.user_id}/{self.user_token}')
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.location, f'/signup')
        response = self.client.get(response.location)
        self.assertIn(b'Invalid or expired token', response.data)
        self.user = models.storage.access(self.user_id, 'id', user_id)
        self.assertIsNone(self.user)
    
    @patch.object(Notifications, 'is_valid')
    @patch.object(Notifications, 'send_Grid')
    def test_Signup(self, mock_send_Grid, mock_is_valid):
        mock_is_valid.return_value = True
        mock_send_Grid.return_value = True
        csrf_token = self.get_csrf_token(self.client.get('/signup').data)
        form_data = MultiDict({
            'username': 'testuser',
            'email': 'testuser@example.com',
            'password': 'password123',
            'confirm_password': 'password123',
            'csrf_token': csrf_token
        })
        maildata = {'url': mock.ANY, 'message': mock.ANY,
                        'subject': mock.ANY, 'header': mock.ANY,
                        'username': 'testuser', 'email':'testuser@example.com',
                        'id': mock.ANY
                        }
        builder = EnvironBuilder(method='POST', data=form_data)
        env = builder.get_environ()
        env['HTTP_REFERER'] = 'http://127.0.0.1:5000/signup'

        with self.client.application.test_request_context():
            response = self.client.post('/signup', data=form_data)
            ID = response.location.split('=')[1]

            self.assertEqual(response.status_code, 302)
            self.assertEqual(response.location, f'/signup?ID={ID}')
            response = self.client.get(response.location)
            self.assertIn(b"""An email has been sent to testuser@example.com to complete your registration""", response.data)

            self.assertEqual(models.redis_storage.get_list(ID)[0]['id'], ID)
            user_data = models.redis_storage.get_list(ID)[0]
            self.assertEqual(user_data['Username'], form_data['username'])
            self.assertEqual(user_data['Email'], form_data['email'])
            self.assertTrue(mock_send_Grid.called)
            self.assertTrue(mock_is_valid.called)
            mock_is_valid.assert_called_once_with(user_data['Email'])
            mock_send_Grid.assert_called_once_with(None, **maildata)
            models.redis_storage.delete(ID)
            self.assertEqual(models.redis_storage.get_list(ID), [])

    def test_logout(self):
        response = self.client.get('/logout')
        self.assertEqual(response.status_code, 302)
        with self.client.session_transaction() as session:
            self.assertNotIn('id', session)
        self.assertEqual(response.location, '/login?next=%2Flogout')

    @patch.object(user_id, 'get_reset_token', return_value='test_token')
    @patch.object(Notifications, 'send_Grid', return_value=True)
    def test_reset_password(self, mock_send_Grid, mock_get_reset_token):
        response = self.client.get('/reset')
        self.assertEqual(response.status_code, 200)
        csrf_token = self.get_csrf_token(self.client.get('/reset').data)
        form_data = MultiDict({
            'email': 'adavaonimisi@gmail.com',
            'csrf_token': csrf_token
        })
        user = models.storage.access(form_data['email'], 'Email', user_id)
        maildata = {'url': url_for('Main.reset_token',
                                       token='test_token', _external=True),
                    'message':f'''To reset your password, kindly visit the following link:''',
                    'subject': 'Password Reset Request',
                    'header': 'Password Reset'}
        builder = EnvironBuilder(method='POST', data=form_data)
        env = builder.get_environ()
        env['HTTP_REFERER'] = 'http://127.0.0.1:5000/reset'
        
        with self.client.application.test_request_context():
            response = self.client.post('/reset', data=form_data)
            #ID = response.location.split('=')[1]
            self.assertEqual(response.status_code, 302)
            self.assertEqual(response.location, '/login')
            self.assertTrue(mock_send_Grid.called)
            mock_get_reset_token.assert_called_once_with()
            mock_send_Grid.assert_called_once_with(user, **maildata)

    @patch.object(user_id, 'verify_reset_token')
    def test_reset_token_validity(self, mock_verify_reset_token):
        user = models.storage.access('adavaonimisi@gmail.com', 'Email', user_id)
        #token = "test_token"
        mock_verify_reset_token.return_value = user
        token = user.get_reset_token()
        response = self.client.post(f'reset/{token}',
                                    data={'password': 'newpassword6253',
                                          'confirm_password': 'newpassword6253'})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.location, '/login')





if __name__ == '__main__':
    unittest.main()
