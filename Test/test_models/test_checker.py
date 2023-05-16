#!/usr/bin/env python3
"""
    Test cases for the checker module.
"""
import unittest
import os
from models.checker import Checker
from unittest.mock import patch, MagicMock
from models.baseModel import user_id
from parameterized import parameterized


class TestChecker(unittest.TestCase):
    """
        Test cases for the checker module.
    """
    def setUp(self):
        """
            Setup for all the test cases creates instance of Checker class.
        """
        self.ID = 105
        self.checker = Checker(self.ID)

    def tearDown(self):
        pass

    @parameterized.expand([
        ({"True": {"question1": "just testing", "question2": "just testing"},
          "False": {"question3": "just testing false answers", 
                    "question4": "just testing false answers",
                    "question5": "just testing false answers"}}, 40.0)
    ])
    def test_check_answers(self, data, expected_result):
        """
            Test case for check_answers method.
        """
        schedule_id = 114
        average = Checker.check_answers(data, self.ID, schedule_id)
        self.assertEqual(average, expected_result)


    def test_invoke_chatbot_with_invalid_input(self):
        """
            Test case for _invoke_chatbot method with invalid input.
        """
        with self.assertRaises(ValueError):
            Checker._invoke_chatbot("invalid data")
    

    @parameterized.expand([
        (
            {
                67: {"question1": "answer1", "question2": "answer2"}
            },
         {
            "True": {'question1': 'answer1', 'question2': 'answer2'},
            "False": {}
        })
    ])
    def test_invoke_chatbot_success(self, data, expected_response):
        """
            Test case for _invoke_chatbot method with valid input.
        """
        with patch.dict(os.environ, {'OPENAI_API_KEY': 'my_api_key'}):
            with patch('openai.Completion.create') as mock_create:
                mock_create.return_value.choices = [
                    type('', (), {'text': 'True'})(),
                    type('', (), {'text': 'False'})()
                ]
                result = Checker._invoke_chatbot(data)
                self.assertEqual(result, expected_response)

    @parameterized.expand([
        ({67: {"question1": "answer1", "question2": "answer2"}},
        {"True": {}, "False": {} })
    ])
    def test_invoke_chatbot_invalid_response(self, data, expected_response):
        """
            Test case for _invoke_chatbot method with invalid response.
        """
        with patch.dict(os.environ, {'OPENAI_API_KEY': 'my_api_key'}):
            with patch('openai.Completion.create') as mock_create:
                mock_create.return_value.choices = []
                result = Checker._invoke_chatbot(data)
                self.assertEqual(result, expected_response)

    def test_invoke_chatbot_exception(self):
        """
            Test case for _invoke_chatbot method with exception.
        """
        data = {
                67: {"question1": "answer1", "question2": "answer2"}
            }
        with patch.dict(os.environ, {'OPENAI_API_KEY': 'my_api_key'}):
            with patch('openai.Completion.create') as mock_create:
                mock_create.side_effect = Exception()
                with self.assertRaises(Exception) as cm:
                    Checker._invoke_chatbot(data)
                self.assertEqual(str(cm.exception), 'Error invoking chatbot ')
    
    def test_help(self):
        """
            Test case for Help method. that sends a message to the chatbot.
            and returns the response.
        """
        message = "What can you recommend for me today?"
        expected_response = "Some recommendation"
        usr = user_id()
        usr.save_history = False
        with patch("models.checker.openai.ChatCompletion.create") as mock_chat, \
             patch("models.storage.access") as mock_access, \
             patch("models.redis_storage.get_list") as mock_get_list, \
             patch("models.redis_storage.set_dict") as mock_set_dict:
            mock_chat.return_value = {"choices": [
                {"message": {"content": expected_response}}
                ]}
            mock_access.return_value = usr
            mock_get_list.return_value = [{"role": "user", "content":
                                           message, "ID": self.ID}]
            result = self.checker.Help(message)
            mock_chat.assert_called_once()
            mock_access.assert_called_once()
            mock_get_list.assert_called_once()
            mock_set_dict.assert_called_once()
            self.assertEqual(result, expected_response)


    def test_help_with_error(self):
        """
            Test case for Help method. validates that an exception is raised.
            when the chatbot returns an error.
        """
        message = "What can you recommend for me today?"
        usr = user_id()
        usr.save_history = False
        with patch("models.checker.openai.ChatCompletion.create") as mock_chat, \
             patch("models.storage.access") as mock_access, \
             patch("models.redis_storage.get_list") as mock_get_list, \
             patch("models.redis_storage.set_dict") as mock_set_dict:
            mock_chat.side_effect = Exception("Some error")
            mock_access.return_value = usr
            mock_get_list.return_value = [{"role": "user",
                                           "content": message, "ID": self.ID}]
            with self.assertRaises(Exception) as cm:
                self.checker.Help(message)
            self.assertEqual(str(cm.exception), 'Error invoking chatbot Some error')
