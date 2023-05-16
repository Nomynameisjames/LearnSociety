import unittest
import os
from models.baseModel import user_id, User
from redis import Redis
from unittest.mock import patch, Mock
from models import storage, redis_storage
from models.engine.DB_storage import DBstorage, Base
from models.engine.RedisDB_storage import Cache

"""
   test class for the Redis DB connection
"""
class Test_RedisDB_Storage(unittest.TestCase):

    def setUp(self):
        """
            create a new RedisDBstorage instance for each test case
        """
        self.cache = Cache()

    def tearDown(self):
        """
            close the RedisDBstorage connection after each test case and
            delete the test key
        """
        self.cache.delete('test_key')

    def test_get_cache_with_cache(self):
        """
            test the get method with a key that exists in the cache
        """
        with patch.object(self.cache, 'get') as mock_get:
            mock_get.return_value = b'test_value'
            result = self.cache.get('test_key')
            mock_get.assert_called_with('test_key')
            self.assertEqual(result, b'test_value', 'Get cache passed')

    def test_set_cache(self):
        """
            test the set method with a key that exists in the cache
        """
        with patch.object(self.cache, 'set') as mock_set:
            mock_set.return_value = True
            result = self.cache.set('test_key', 'test_value')
            mock_set.assert_called_with('test_key', 'test_value')
            self.assertTrue(result, 'Set cache passed')
            

    def test_delete_cache(self):
        """
            test the delete method with a key that exists in the cache
        """
        with patch.object(self.cache, 'delete') as mock_delete:
            mock_delete.return_value = True
            result = self.cache.delete('test_key')
            self.assertTrue(result)
            mock_delete.assert_called_once_with('test_key')

    def test_delete_list_item(self):
        """
            test the delete_list_item method with a key that exists in the cache
        """
        with patch.object(self.cache, 'delete_list_item') as mock_lrem:
            mock_lrem.return_value = True
            result = self.cache.delete_list_item('test_key', 'test_value')
            self.assertTrue(result)
            mock_lrem.assert_called_once_with('test_key','test_value')
    
    def test_delete_list_dict_item(self):
        """
            test the delete_list_dict_item method with a key that exists in the
            cache
        """
        with patch.object(self.cache, 'delete_list_dict_item') as mock_lrem:
            mock_lrem.return_value = True
            result = self.cache.delete_list_dict_item('test_key','test_value')
            self.assertTrue(result)
            mock_lrem.assert_called_once_with('test_key', 'test_value')

    def test_exists_cache(self):
        """
            test the exists method and validate that a key exists in the cache
        """
        with patch.object(self.cache, 'exists') as mock_exists:
            mock_exists.return_value = True
            result = self.cache.exists('test_key')
            self.assertTrue(result)
            mock_exists.assert_called_once_with('test_key')

    def test_cache_timeout(self):
        """
            test the set time out method and validate that a key in the
            cache is removed after the specified time
        """
        with patch.object(self.cache, 'set_dict') as mock_timeout:
            mock_timeout.return_value = True
            result = self.cache.set_dict('test_key', 'test_value', 10)
            self.assertTrue(result)
            mock_timeout.assert_called_once_with('test_key', 'test_value', 10)



@unittest.skipIf(os.getenv('STORAGE_TYPE') != 'mysqlDB' and
                 os.getenv('MYSQL_TEST_DB') != "BotSchedule_test_DB",
                 'not using db')
class Test_MYSQLDB_Storage(unittest.TestCase):
    """
        class for testing the MySQL DB connection
    """
    
    @classmethod
    def setUpClass(cls):
         # create the database engine and tables

         print('\n\n.................................')
         print('..... Testing Documentation .....')
         print('..... For DB Storage Class .....')
         print('.................................\n\n')
        
    @classmethod
    def tearDownClass(cls):
         # drop all tables and close the database engine
        #cls.DBstorage._DBstorage__session.close()
        pass

    def setUp(self):
       # create a new session and DBstorage instance for each test case
        self.storage = storage
        
    def tearDown(self):
        # rollback any uncommitted changes and close the session
        self.storage.rollback_session()
        self.storage.close()
    
    def test_new(self):
        """
            validate that a new object is added to the database
            when the new method is called
        """
        # create a test user and schedule
        user = user_id(id=103,
                       User_name="Raggedpriest",
                       Password="23443",
                       Email="example@testing.com",
                       Phone_number="23443",
                       save_history=0,
                       Created_at=None
                       )

        self.storage.new(user)
        self.storage.save()
        retrieved_obj = self.storage.access(user.Email, "Email", user_id)
        self.assertEqual(retrieved_obj, user)

    def test_delete(self):
        """
            validate that an object is deleted from the database
            when the delete method is called
        """
        # create a test user and schedule
        retrieved_obj = self.storage.access(103, "id", user_id)
        self.storage.delete(retrieved_obj)
        self.storage.save()
        retrieved_obj = self.storage.access(103, "id", user_id)
        self.assertEqual(retrieved_obj, None)
    

    def test_view(self):
        """
            validates that a user and schedule are returned when the view
            method is called
        """
        # create a test user and schedule
        ID = 103
        retrieved_obj = self.storage.view(ID)
        self.assertIsInstance(retrieved_obj, tuple, "validate the view method returns a list of objects")
        self.assertEqual(len(retrieved_obj), 2, "validate the view method returns a tuple of objects")
        self.assertIsInstance(retrieved_obj[0].get(str(ID)), user_id, "validate obj is instance of user_id")
        self.assertIsInstance(retrieved_obj[1], dict, "validate obj is instance of User")

        



if __name__ == '__main__':
    unittest.main(argv=['first-arg-is-ignored'], defaultTest='Test_MYSQLDB_Storage')
