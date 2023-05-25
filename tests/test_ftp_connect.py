import os
import unittest
import socket

from dotenv import load_dotenv, find_dotenv

from ftp_client.connect import Connection


class TestFTPConnection(unittest.TestCase):
    """
    This class contains unit tests for the `Connection` class in the FTP Connection module.
    """
    def setUp(self):
        """
        Initializes the Connection object for testing.
        """
        load_dotenv(find_dotenv('config.env'))
        self.password = os.getenv('FTP_PASS')
        self.username = os.getenv('FTP_USER')
        self.host = os.getenv('FTP_HOST')
        self.conn = Connection()

    def test_connect_success(self):
        """
        Tests that the `connect` method returns the response code if successful.
        """
        response = self.conn.connect('ftp.dlptest.com')
        self.assertTrue(response)
        self.conn.close()

    def test_connect_failure(self):
        """
        Tests that the `connect` method returns False if the connection fails.
        """
        response = self.conn.connect('invalid.host')
        self.assertFalse(response)

    def test_close(self):
        """
        Tests that the `close` method closes the connection to the server.
        """
        self.conn.connect('ftp.dlptest.com')
        self.conn.close()
        self.assertFalse(self.conn.connected)

    def test_send_request(self):
        """
        Tests that the `send_request` method sends a request to the server.
        """
        self.conn.connect('ftp.dlptest.com')
        self.conn.send_request('USER username')
        response = self.conn.get_response()
        self.assertEqual(response['code'], '331')
        self.conn.close()

    def test_get_response(self):
        """
        Tests that the `get_response` method receives a response from the server.
        """
        self.conn.connect('ftp.dlptest.com')
        self.conn.send_request('USER username')
        response = self.conn.get_response()
        self.assertEqual(response['code'], '331')
        self.conn.close()

    def test_parse_response(self):
        """
        Tests that the `_parse_response` method returns a dictionary with the response code,
        message, and error status.
        """
        response = self.conn._parse_response('331 User name okay, need password.')
        self.assertEqual(response['code'], '331')
        self.assertEqual(response['message'], 'User name okay, need password.')
        self.assertFalse(response['error'])

    def test_create_pasv_con(self):
        """
        Tests that the `create_pasv_con` method creates a connection to the specified host and port.
        """
        self.conn.connect('ftp.dlptest.com')
        self.conn.send_request('USER dlpuser')
        self.conn.get_response()
        self.conn.send_request('PASS rNrKYTX9g7z3RgJRmxWuGHbeu')
        self.conn.get_response()
        file_con = self.conn.create_pasv_con()
        self.assertIsInstance(file_con, socket.socket)
        self.conn.close()


if __name__ == '__main__':
    unittest.main()
