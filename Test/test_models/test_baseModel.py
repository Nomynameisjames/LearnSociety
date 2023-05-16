#!/usr/bin/env python3
"""Unittest for BaseModel class"""
import unittest
import json
import time
import os
from models.baseModel import user_id
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock


class TestBaseModel(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        pass

    @classmethod
    def tearDownClass(cls):
        """
            Remove the created json file
        """
        os.remove('encryptFile.json')

    def setUp(self):
        """
            Create a new instance of user_id class
        """
        self.model = user_id()

    def tearDown(self):
        # remove the created json file
        #os.remove('encryptFile.json')
        pass
    
    def test_get_reset_token(self):
        """
            Test the get_reset_token method of user_id class
            and return a token
        """
        ID = 'test_user_id'
        user = user_id(id=ID)
        with patch('models.storage.access', return_value=user):
            token = user.get_reset_token()
            self.assertIsNotNone(token)
            self.assertEqual(token, user.get_reset_token())
    
    def test_get_reset_token_user_not_found(self):
        """
            Test the get_reset_token method of user_id class raises an exception
            when user is not found
        """
        ID = 'test_user_id'
        user = None
        with patch('models.storage.access', return_value=user):
            with self.assertRaises(Exception):
                user_id(id=ID).get_reset_token()

    def test_verify_reset_token(self):
        """
            Test the verify_reset_token method of user_id class
            and return a user
        """
        token = "some_token_string"
        ID = "some_user_id"
        with patch("models.baseModel.jwt.decode") as mock_decode, \
             patch("models.storage.access") as mock_access, \
             patch("models.baseModel.jwt.InvalidTokenError"), \
             patch("models.baseModel.jwt.ExpiredSignatureError"):
            mock_decode.return_value = {"user_id": ID}
            mock_access.return_value = {"id": ID}
            result = user_id.verify_reset_token(token)
            self.assertEqual(result, {"id": ID})
    
    def test_generate_confirmation_code(self):
        """
            Test the generate_confirmation_code method of user_id class
            and return a code and expiration time
        """

        code, expiration_time = self.model.generate_confirmation_code()

        self.assertIsInstance(code, str)
        self.assertEqual(len(code), 8)

        self.assertIsInstance(expiration_time, float)
        self.assertGreater(expiration_time, time.time())

        with open('encryptFile.json', 'r') as f:
            data = json.load(f)

        self.assertEqual(data['code'], code)
        self.assertEqual(data['expiration_time'], expiration_time)

    def test_verify_confirmation_code(self):
        """
            Test the verify_confirmation_code method of user_id class
            and return True or False depending on the code validity
        """
        with open('encryptFile.json', 'r') as f:
            data = json.load(f)
        code = data['code']
        result = user_id.verify_confirmation_code(code)
        self.assertTrue(result)
        
        result = user_id.verify_confirmation_code('wrongcode')
        self.assertFalse(result)

if __name__ == '__main__':
    unittest.main()
