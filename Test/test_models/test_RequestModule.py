#!/usr/bin/env python3
"""
    This module tests the RequestModule module.
"""
import unittest
import os
import requests.exceptions
import requests
from unittest.mock import MagicMock, patch, Mock
from models.RequestModule import SearchBar


class TestSearchBar(unittest.TestCase):
    """
        This class tests the SearchBar class in the RequestModule module.
    """

    def setUp(self):
        """
            method creates an instance of the SearchBar object for testing.
        """
        self.search_bar = SearchBar()

    def tearDown(self):
        pass

    def test_wikipedia_with_valid_search(self):
        """
            method tests the wikipedia method with a valid search term.
        """
        expected_summary = 'This is a summary of the search result.'
        mock_page = MagicMock()
        mock_page.summary = expected_summary
        wikipedia_mock = MagicMock()
        wikipedia_mock.suggest.return_value = None
        wikipedia_mock.search.return_value = ['result 1']
        wikipedia_mock.page.return_value = mock_page
        with patch('models.RequestModule.wikipedia', wikipedia_mock):
            summary = self.search_bar.Wikipedia('valid search term')
            self.assertEqual(summary, expected_summary)

    def test_wikipedia_with_suggestion(self):
        """
            method tests the wikipedia method with a misspelled search term.
            to validate suggestion functionality.
        """
        expected_summary = 'This is a summary of the search result.'
        mock_page = MagicMock()
        mock_page.summary = expected_summary
        wikipedia_mock = MagicMock()
        wikipedia_mock.suggest.return_value = 'suggested search term'
        wikipedia_mock.search.return_value = ['result 1']
        wikipedia_mock.page.return_value = mock_page
        with patch('models.RequestModule.wikipedia', wikipedia_mock):
            summary = self.search_bar.Wikipedia('misspelled search term')
            self.assertEqual(summary, expected_summary)
            wikipedia_mock.suggest.assert_called_once_with('misspelled search term')
            wikipedia_mock.search.assert_called_once_with('suggested search term', results=5)
            wikipedia_mock.page.assert_called_once_with('result 1')


    @patch('models.RequestModule.requests')
    def test_get_wiki_briefs(self, mock_requests):
        """
            method tests the get_wiki_briefs method. by making sure that
            requests.request is called with the correct arguments and that
            the method returns the correct result.
        """
        # Set up mock response for requests.request
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"result": ["brief 1", "brief 2",
                                                      "brief 3"]}
        mock_requests.request.return_value = mock_response

        # Set up SearchBar object and call get_wiki_briefs method
        result = self.search_bar.get_wiki_briefs("test search")
        url = "https://wiki-briefs.p.rapidapi.com/search"
        code = os.environ.get('RapidAPI')
        HOST = "wiki-briefs.p.rapidapi.com"
        headers = {
                "X-RapidAPI-Key": str(code),
                "X-RapidAPI-Host": HOST
            }
        params = {"q": "test search", "topk": "3"}
        # Assert that requests.request was called with the correct arguments
        mock_requests.request.assert_called_once_with("GET", url,
                                                      headers=headers,
                                                      params=params)

        # Assert that the method returns the correct result
        self.assertEqual(result, {"result": ["brief 1", "brief 2", "brief 3"]})
    
    @unittest.skip("Skipping test_get_wiki_briefs_exception")
    @patch('models.RequestModule.requests') 
    def test_get_wiki_briefs_exception(self, mock_requests):
        """
            method tests the get_wiki_briefs method. and assert that it raises
            an exception when requests.request returns a status code other
            than 200.
        """
        # Set up mock response for requests.request
        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.text = "Server error"
        mock_requests.request.return_value = mock_response

        # Set up SearchBar object and call get_wiki_briefs method
        with self.assertRaises(Exception):
            self.search_bar.get_wiki_briefs("test search")


    @patch('models.RequestModule.requests')
    def test_get_recommendations(self, mock_requests):
        """
            method tests the get_recommendations method. by making sure that
            requests.get is called with the correct arguments and that
            the method returns the correct result.
        """
        # Set up mock response for requests.get
        mock_response = Mock()
        mock_response.status_code = 200
        content = b"<html><body><a class='reference internal'href=\
                'datastructures.html'>5. Data Structures</a></body></html>"
        mock_response.content = content
        mock_requests.get.return_value = mock_response

        # Set up SearchBar object and call get_recommendations method
        result = self.search_bar.get_recommendations("Data Structure")

        # Assert that requests.get was called with the correct arguments
        url = "https://docs.python.org/3/tutorial/index.html"
        mock_requests.get.assert_called_once_with(url)

        # Assert that the method returns the correct result
        expected = [
                    {
                    'topic': '5. Data Structures', 'link':'datastructures.html'
                    }
                ]
        self.assertEqual(result, expected)

    @patch('models.RequestModule.requests')
    def test_get_recommendations_with_error(self, mock_requests):
        """
            method tests the get_recommendations method. and assert that it
            returns an error message when requests.get raises an exception.
        """
        # Set up mock response for requests.get
        mock_response = Mock()
        mock_response.side_effect = Exception("error")
        mock_requests.get.return_value = mock_response

        # Set up SearchBar object and call get_recommendations method
        result = self.search_bar.get_recommendations("test search")

        # Assert that requests.get was called with the correct arguments
        url = "https://docs.python.org/3/tutorial/index.html"
        mock_requests.get.assert_called_once_with(url)

        # Assert that the method returns an error message
        self.assertEqual(result, "There was a problem: object of type 'Mock' has no len()")


    def test_get_resource_with_valid_task(self):
        """
            method tests the get_resource method. by making sure that
            requests.get is called with the correct arguments and that
            the method returns the correct result.
        """
        # mock the requests.get method to return a successful response
        with patch('models.RequestModule.requests.get') as mock_get:
            mock_response = Mock()
            mock_response.status_code = 200
            content = b'''<html><body><section><h1>Title</h1><p>Paragraph</p>
                        </section></body></html>'''
            mock_response.content = content
            mock_get.return_value = mock_response

            # call the method with a valid task
            task = [
                    {
                        'topic': '5. Data Structures', 'link':
                        'datastructures.html'
                    }
                ]
            result = self.search_bar.get_resource(task)

            # check if the method returns a list with section data
            expected_result = [{
                                'title': 'Title', 'content': [
                                    {'type': 'paragraph', 'text': 'Paragraph'}
                                    ]
                                }]
            self.assertEqual(result, expected_result)


    def test_get_resource_with_invalid_task(self):
        """
            method tests the get_resource method. and assert that it
            returns an error message when requests.get raises an exception
            or when the task is invalid.
        """
        # call the method with an invalid task
        task = [
                {
                    'topic': '', 'link': ''
                }
            ]
        result = self.search_bar.get_resource(task)

        # check if the method returns an error message
        expected_result = 'No link found'
        self.assertEqual(result, expected_result)

    def test_get_resource_with_other_error(self):
        # mock the requests.get method to raise a ConnectionError
        mock_get = MagicMock()
        mock_get.side_effect = ConnectionError()
        with patch('models.RequestModule.requests.get', mock_get):
            mock_get.side_effect = ConnectionError()

            # call the method with a valid task
            task = task = [{'link': 'example'}]
            result = self.search_bar.get_resource(task)

            # check if the method returns an error message
            expected_result = f'Connection Error: {ConnectionError()}'
            self.assertEqual(result, expected_result)

    def test_get_resource_with_http_error(self):
        """
            method tests the get_resource method. and assert that it
            returns an error message when requests.get raises an HTTPError.
        """
        # mock the requests.get method to raise an HTTPError
        mock_get = MagicMock()
        response = requests.models.Response()
        response.status_code = 404
        response._content = b"Not Found"
        mock_get.return_value = response

        with patch('models.RequestModule.requests.get', mock_get):
            task = [{'link': 'example'}]
            result = self.search_bar.get_resource(task)

            # check if the method returns an error message
            expected_result = 'There was a problem: 404 Client Error: None for url: None'
            self.assertEqual(result, expected_result)



if __name__ == '__main__':
    unittest.main()
