import os
import unittest

import requests
from dotenv import load_dotenv, find_dotenv
from webdav_api_client.connect import Connection


class TestWebdavConnect(unittest.TestCase):
    """
       This class contains unit tests for the `Connection` class.
    """
    def setUp(self):
        """
        Set up a Connection object for testing.
        """
        load_dotenv(find_dotenv('config.env'))
        self.password = os.getenv('WEBDAW_PASS')
        self.username = os.getenv('WEBDAW_USER')
        self.connection = Connection(cloud_type='yadisk')

    def test_init(self):
        """
        Tests that the `Connection` class can be instantiated.
        """
        connection = Connection(cloud_type='yadisk')
        self.assertIsInstance(connection, Connection)

    def test_send_request_username_password(self):
        """
        Tests that the `send_request` method returns a response when a username and password are
        provided.
        """
        self.connection.username = self.username
        self.connection.password = self.password
        response = self.connection.send_request("GET")
        self.assertIsInstance(response, requests.Response)


    def test_send_request_add_url(self):
        """
        Tests that the `send_request` method returns a response with the correct URL when an
        additional URL is provided.
        """
        self.connection.username = self.username
        self.connection.password = self.password
        response = self.connection.send_request("GET", add_url="path/to/resource")
        self.assertEqual(response.url, "https://webdav.yandex.ru/path/to/resource")

    def test_send_request_data(self):
        """
        Tests that the `send_request` method returns a response with the data included in the request body.
        """
        self.connection.username = self.username
        self.connection.password = self.password
        data = {"key": "value"}
        response = self.connection.send_request("POST", data=data)
        self.assertEqual(response.request.body, 'key=value')


if __name__ == '__main__':
    load_dotenv(find_dotenv('config.env'))
    unittest.main()
