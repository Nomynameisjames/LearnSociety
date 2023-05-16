import unittest
from flask_testing import TestCase
from web_flask.app import app
import os

class MyTest(TestCase):
    """
        Test cases for CSRF protection
    """
    def create_app(self):
        """
            Create an instance of the app with the testing configuration
        """
        app.config['WTF_CSRF_ENABLED'] = True
        app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
        return app
    
    def test_csrf_protected_form(self):
        """
            Test that the login form includes a CSRF token
        """
        # create a client to make requests to the app
        client = self.client
        
        # make a GET request to the login page to get the CSRF token
        response = client.get('http://127.0.0.1:5000/login')
        csrf_token_input = response.data.decode('utf-8')
        #csrf_token = response.soup.find('input', {'name': 'csrf_token'}).get('value')
        csrf_token = csrf_token_input.split('name="csrf_token" type="hidden" value="')[1].split('">')[0]
        
        # make a POST request to the login page without including the CSRF token
        response = client.post('/login', data={
            'email': 'testing@gmail.com',
            'password': 'PASSWORD'
        })
        
        # check that the response includes an error message indicating the CSRF token is missing
        self.assertIn(b'Missing CSRF token', response.data, f'''Checks that the
                                            response includes an error message
                                        indicating the CSRF token is missing''')

    def test_csrf_token(self):
        """
            Test that the login form includes a CSRF token and displays
            a success message when the correct credentials are provided
        """
        # create a client to make requests to the app
        client = self.client

        # make a GET request to the login page to get the CSRF token
        response = client.get('http://127.0.0.1:5000/login')
        csrf_token_input = response.data.decode('utf-8')
        csrf_token = csrf_token_input.split('name="csrf_token" type="hidden" value="')[1].split('">')[0]

        # check that a CSRF token was generated
        self.assertIsNotNone(csrf_token)

        # make a POST request to the login page including the CSRF token
        response = client.post('http://127.0.0.1:5000/login', data={
            'email': 'adavaonimisi@gmail.com',
            'password': 'PASSWORD',
            'csrf_token': csrf_token
        }, follow_redirects=True)

        # check that the login was successful and the CSRF token was validated
        self.assert200(response)
        self.assertIn(b'You are logged in!', response.data)

    def test_csrf_token_invalid(self):
        """
            Test that the login form includes a CSRF token and displays
            an error message when the wrong credentials are provided
        """
        # create a client to make requests to the app
        client = self.client
        response = client.get('http://127.0.0.1:5000/login')
        csrf_token_input = response.data.decode('utf-8')
        csrf_token = csrf_token_input.split('name="csrf_token" type="hidden" value="')[1].split('">')[0]

        # make a GET request to the login page to get the CSRF token
        response = client.post('http://127.0.0.1:5000/login', data={
            'email': 'wrongemail@gmail.com',
            'password': 'wrongPASSWORD',
            'csrf_token': csrf_token
        }, follow_redirects=True)

        self.assertIn(b'Login Unsuccessful. Please check username and password', response.data)


if __name__ == '__main__':
    unittest.main()

