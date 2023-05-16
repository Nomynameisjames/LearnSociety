#!/usr/bin/env python3
"""
  import files
"""
import unittest
import smtplib
import os
from models.RequestModule import Notifications
from unittest.mock import patch, MagicMock


class TestNotifications(unittest.TestCase):
    """
        TestNotifications Class 
    """

    def setUp(self):
        """
            setUp creates a new instance of Notifications before each test
        """
        self.notifications = Notifications()

    def tearDown(self):
        """
            tearDown
        """
        pass

    def test_send_email_success(self):
        """
            test_send_email tests that the send_email method returns True
            when the email is sent successfully
        """
        user = MagicMock()
        user.User_name = 'test_user'
        user.Email = 'test@example.com'
        user.generate_confirmation_code.return_value = ('123456', 'token')

        subject = 'Test email'
        message = 'This is a test email'

        with patch.object(smtplib, 'SMTP') as mock_smtp:
            mock_server = MagicMock()
            #mock_smtp.return_value = mock_server
            mock_smtp.return_value.__enter__.return_value = mock_server

            result = self.notifications.send_email(user, subject, message)

            mock_smtp.assert_called_once_with(self.notifications.server,
                                              self.notifications.port)
            mock_server.ehlo.assert_called_once()
            mock_server.starttls.assert_called_once()
            mock_server.login.assert_called_once_with(
                    self.notifications.sender_email,
                    self.notifications.password)
            mock_server.sendmail.assert_called_once_with(
                    self.notifications.sender_email, user.Email,
                    f"Subject: {subject}\n\nHello {user.User_name},\n\n{message}\n\n123456")
            self.assertTrue(result)

    def test_send_email_error(self):
        """
            test_send_email tests that the send_email method returns False
            when the email is not sent successfully and logs the error
        """
        user = MagicMock()
        user.generate_confirmation_code.return_value = ('123456', 'token')

        subject = 'Test email'
        message = 'This is a test email'

        with patch.object(smtplib, 'SMTP') as mock_smtp:
            mock_smtp.side_effect = Exception('SMTP error')

            result = self.notifications.send_email(user, subject, message)

            self.assertEqual(result, 'error SMTP error')

    @patch('models.RequestModule.os.environ.get')
    @patch('models.RequestModule.requests.request')
    @patch('models.RequestModule.Environment.get_template')
    def test_send_Grid(self, mock_get_template, mock_request, mock_environ_get):
        """
            test_send_Grid tests that the send_Grid method returns True
            when the email is sent successfully
        """
        # Mock environment variables
        mock_environ_get.side_effect = lambda key: {
            'FILE_PATH': '/path/to/templates',
            'RapidAPI': 'your-rapidapi-key',
        }.get(key)
        
        # Mock user object
        user = MagicMock(User_name='John Doe', Email='johndoe@example.com')
        
        # Mock arguments
        kwargs = {
            'url': 'http://example.com/verify',
            'message': 'Hello world!',
            'header': 'Test email',
            'username': 'John Doe',
            'email': 'johndoe@example.com',
            'subject': 'Test email',
        }
        
        # Mock template rendering
        mock_template = MagicMock()
        mock_template.render.return_value = '<html><body>{{ file }}</body></html>'
        mock_get_template.return_value = mock_template
        
        # Call the method
        result = self.notifications.send_Grid(user=user, **kwargs)
        
        # Assert that the method returned True
        self.assertTrue(result)
        
        # Assert that the template was rendered with the correct arguments
        mock_template.render.assert_called_once_with(file=[
            'Hello world!', 'Test email', 'John Doe'],
                                                     url='http://example.com/verify')
        
        # Assert that the request was made with the correct parameters
        mock_request.assert_called_once_with(
            'POST',
            'https://rapidprod-sendgrid-v1.p.rapidapi.com/mail/send',
            json={
                'personalizations': [
                    {
                        'to': [{'email': 'johndoe@example.com'}],
                        'subject': 'Test email',
                    }
                ],
                'from': {'email': self.notifications.sender_email},
                'content': [
                    {
                        'type': 'text/html',
                        'value': "<html><body>{{ file }}</body></html>",
                    }
                ],
            },
            headers={
                'content-type': 'application/json',
                'X-RapidAPI-Key': 'your-rapidapi-key',
                'X-RapidAPI-Host': 'wiki-briefs.p.rapidapi.com',
            }
        )

    
    def test_send_Grid_exception(self):
        """
            test_send_Grid_exception tests that the send_Grid method returns
            False when an exception is raised and logs the error
        """
        with patch('models.RequestModule.requests') as mock_requests:
            mock_requests.request.side_effect = Exception('test exception')
            with self.assertRaises(ValueError) as cm:
                self.notifications.send_Grid(user=None, 
                                             message='test message',
                                             subject='test subject')
            self.assertIn('Error sending email', str(cm.exception))

    def test_is_valid_valid_email(self):
        """
            test_is_valid_valid_email tests that the is_valid method returns
            True when the email is valid
        """
        # Arrange
        email = 'test@example.com'
        expected_output = True

        # Mock requests.get
        mocked_response = MagicMock()
        mocked_response.status_code = 200
        mocked_response.json.return_value = {
            'format_valid': True,
            'mx_found': True,
            'smtp_check': True,
            'state': 'deliverable'
        }
        with patch('models.RequestModule.requests.get',
                   return_value=mocked_response):
            # Act
            result = self.notifications.is_valid(email)

            # Assert
            self.assertEqual(result, expected_output)

    def test_is_valid_invalid_email(self):
        """
            test_is_valid_invalid_email tests that the is_valid method returns
            False when the email is invalid
        """
        # Arrange
        email = 'notanemail'
        expected_output = False

        # Mock requests.get
        mocked_response = MagicMock()
        mocked_response.status_code = 400
        with patch('models.RequestModule.requests.get',
                   return_value=mocked_response):
            # Act
            result = self.notifications.is_valid(email)

            # Assert
            self.assertEqual(result, expected_output)

    def test_is_valid_connection_error(self):
        """
            test_is_valid_connection_error tests that the is_valid method
            returns False when a ConnectionError is raised
        """
        # Arrange
        email = 'test@example.com'
        expected_output = False

        # Mock requests.get to raise a ConnectionError
        with patch('models.RequestModule.requests.get', side_effect=ConnectionError):
            # Act
            result = self.notifications.is_valid(email)

            # Assert
            self.assertEqual(result, expected_output)


if __name__ == '__main__':
    unittest.main()
