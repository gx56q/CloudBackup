import os
import unittest
from unittest.mock import patch, MagicMock, Mock, call

from dotenv import find_dotenv, load_dotenv

from ftp_client.connect import Connection
from ftp_client.ftpclient import FtpClient


class TestFtpClient(unittest.TestCase):
    """
    This class contains unit tests for the `FtpClient` class.
    """

    def setUp(self):
        load_dotenv(find_dotenv('config.env'))
        self.password = os.getenv('FTP_PASS')
        self.username = os.getenv('FTP_USER')
        self.host = os.getenv('FTP_HOST')
        self.host = os.getenv('FTP_HOST')
        self.client = FtpClient()
        self.client.connection = MagicMock()

    def test_init_default_values(self):
        ftp_client = FtpClient()
        self.assertIsInstance(ftp_client.connection, Connection)
        self.assertEqual(ftp_client.transfer_type, ('I', 'binary'))
        self.assertFalse(ftp_client.logged_in)

    def test_connect_invalid_host(self):
        client = FtpClient()
        user = self.username
        password = self.password
        with self.assertRaises(SystemExit):
            client.connect("invalidhost", user, password)

    def test_connect_invalid_password(self):
        client = FtpClient()
        user = self.username
        password = "invalid_password"
        with self.assertRaises(SystemExit):
            client.connect(self.host, user, password)

    def test_connect_success(self):
        client = FtpClient()
        user = self.username
        password = self.password
        client.connect(self.host, user, password)
        self.assertTrue(client.logged_in)

    @patch('ftp_client.connect.Connection')
    def test_upload_file_success(self, mock_connection):
        mock_connection_instance = mock_connection.return_value
        mock_connection_instance.connected = True
        mock_connection_instance.get_response.return_value = {'code': '150'}

        local_file = 'path/to/local/file.txt'
        remote_file = '/path/to/remote/file.txt'

        with patch('builtins.open', MagicMock()) as mock_open:
            mock_open.return_value.__enter__.return_value = b'mock file content'
            with self.assertRaises(SystemExit):
                self.client.upload_file(local_file, remote_file)

            mock_connection_instance.create_pasv_con.assert_not_called()
            mock_connection_instance.send_request.assert_not_called()
            mock_connection_instance.get_response.assert_not_called()
            mock_connection_instance.get_response.assert_not_called()

    @patch('ftp_client.connect.Connection')
    def test_upload_file_local_file_not_found(self, mock_connection):
        mock_connection_instance = mock_connection.return_value
        mock_connection_instance.connected = True

        local_file = 'path/to/nonexistent/file.txt'
        remote_file = '/path/to/remote/file.txt'
        with self.assertRaises(SystemExit):
            self.client.upload_file(local_file, remote_file)

    @patch('ftp_client.connect.Connection')
    def test_upload_file_connection_not_established(self, mock_connection):
        mock_connection_instance = mock_connection.return_value
        mock_connection_instance.connected = False

        local_file = 'path/to/local/file.txt'
        remote_file = '/path/to/remote/file.txt'

        with self.assertRaises(SystemExit):
            self.client.upload_file(local_file, remote_file)

    @patch('ftp_client.connect.Connection')
    def test_upload_file_invalid_response_code(self, mock_connection):
        mock_connection_instance = mock_connection.return_value
        mock_connection_instance.connected = True
        mock_connection_instance.get_response.return_value = {'code': '200'}

        local_file = 'path/to/local/file.txt'
        remote_file = '/path/to/remote/file.txt'

        with patch('builtins.open', MagicMock()) as mock_open:
            mock_open.return_value.__enter__.return_value = b'mock file content'
            with self.assertRaises(SystemExit):
                self.client.upload_file(local_file, remote_file)

            mock_connection_instance.create_pasv_con.assert_not_called()
            mock_connection_instance.send_request.assert_not_called()
            mock_connection_instance.get_response.assert_not_called()

    @patch('ftp_client.connect.Connection')
    @patch('os.path')
    def test_upload_directory(self, mock_connection, mock_os):
        mock_connection_instance = mock_connection.return_value
        mock_connection_instance.connected = True
        mock_connection_instance.logged_in = True
        local_dir = '/path/to/local/dir'
        remote_dir = '/path/to/remote/dir'
        mock_os.listdir.return_value = ['file1.txt', 'dir1']
        with self.assertRaises(SystemExit):
            self.client.upload_directory(local_dir, remote_dir)

    def test_upload_file(self):
        local_file = 'path/to/local_directory/file.txt'
        remote_file = 'path/to/remote/file.txt'
        self.client._check_connection = MagicMock(return_value=True)
        self.client._check_logged_in = MagicMock(return_value=True)
        self.client.upload_file = MagicMock()
        self.client.upload(local_file, remote_file)
        self.assertEqual(self.client.upload_file.call_count, 1)

    @patch('ftp_client.connect.Connection')
    @patch('os.path')
    def test_upload_nonexistent_local_dir(self, mock_connection, mock_os):
        mock_connection_instance = mock_connection.return_value
        mock_connection_instance.connected = True
        mock_connection_instance.logged_in = True
        local_dir = '/path/to/nonexistent/dir'
        remote_dir = '/path/to/remote/dir'
        mock_os.path.exists.return_value = False
        with patch('builtins.print') as mock_print:
            with self.assertRaises(SystemExit):
                self.client.upload(local_dir, remote_dir)
            mock_print.assert_called_with('You are not currently logged in to a server.')

    @patch('os.path')
    @patch('asyncio.get_event_loop')
    @patch('ftp_client.connect.Connection')
    def test_download_directory_existing_local_dir(self, mock_connection, mock_asyncio, mock_os):
        mock_connection_instance = mock_connection.return_value
        mock_connection_instance.list.return_value = [
            'drwxrwxr-x 2 user group 4096 May 1 10:00 dir1',
            '-rw-rw-r-- 1 user group 2048 May 1 10:00 file1.txt',
            '-rw-rw-r-- 1 user group 3072 May 1 10:00 file2.txt'
        ]
        remote_dir = '/remote/dir'
        local_dir = '/local/dir'
        mock_os.path.exists.return_value = True
        self.client.download_directory(remote_dir, local_dir)
        mock_os.makedirs.assert_not_called()
        mock_asyncio.get_running_loop.assert_not_called()
        mock_asyncio.get_running_loop().run_in_executor.assert_not_called()

    @patch('os.path')
    @patch('asyncio.get_event_loop')
    @patch('ftp_client.connect.Connection')
    def test_download_directory_new_local_dir(self, mock_connection, mock_asyncio, mock_os):
        mock_connection_instance = mock_connection.return_value
        mock_connection_instance.list.return_value = [
            '-rw-rw-r-- 1 user group 2048 May 1 10:00 file1.txt',
            '-rw-rw-r-- 1 user group 3072 May 1 10:00 file2.txt'
        ]
        remote_dir = '/remote/dir'
        local_dir = '/local/dir'

        mock_os.path.exists.return_value = False

        self.client.download_directory(remote_dir, local_dir)

        mock_os.makedirs.assert_not_called()

        mock_connection_instance.download_directory.assert_not_called()
        mock_asyncio.get_running_loop.assert_not_called()
        mock_asyncio.get_running_loop().run_in_executor.assert_not_called()

    @patch('ftp_client.connect.Connection')
    def test_download_nonexistent_file_or_directory(self, mock_connection):
        remote_dir = '/path/to/nonexistent'
        local_dir = '/path/to/local'
        with patch('ftp_client.print'), \
                patch.object(self.client, 'connection') as mock_client_connection:
            with self.assertRaises(SystemExit):
                self.client.download(remote_dir, local_dir)
            mock_client_connection.close.assert_called_once()
            mock_connection.assert_not_called()

    @patch('ftp_client.connect.Connection')
    def test_upload_nonexistent_file_or_directory(self, mock_connection):
        local_dir = '/path/to/nonexistent'
        remote_dir = '/path/to/remote'
        with patch('ftp_client.print'), \
                patch.object(self.client, 'connection') as mock_client_connection:
            with self.assertRaises(SystemExit):
                self.client.upload(local_dir, remote_dir)
            mock_client_connection.close.assert_called_once()
            mock_connection.assert_not_called()

    def test_connect_already_connected(self):
        """
        Tests that the `connect` method returns False if the client is already connected.
        """
        self.client.connection.connected = True
        self.assertFalse(self.client.connect('localhost', 'username', 'password'))

    def test_connect_invalid(self):
        """
        Tests that the `connect` method returns False if the connection fails.
        """
        with patch('ftp_client.connect.Connection.connect', return_value='220'):
            with patch('ftp_client.connect.Connection.get_response', return_value={'code': '230'}):
                with patch('ftp_client.connect.Connection.send_request'):
                    with patch.object(self.client, '_send_pass', return_value=True):
                        self.client.connect('localhost', 'username', 'password')
                        self.assertFalse(self.client.logged_in)

    def test_connect_connection_error(self):
        host = 'ftp.invalidhost.com'
        user = 'username'
        password = 'password'
        self.client.connection.connected = False
        self.client.connection.connect = MagicMock(
            side_effect=ConnectionError('Error: ' + host + ' is not a valid host.'))
        with self.assertRaises(ConnectionError):
            self.client.connect(host, user, password)

    def test_close(self):
        self.client.connection = MagicMock()
        self.client.connection.connected = True
        self.client.connection.send_request.return_value = None
        self.client.connection.get_response.return_value = {'code': '221'}
        self.client.close()
        self.assertFalse(self.client.logged_in)
        self.client.connection.send_request.assert_called_with('QUIT')
        self.client.connection.get_response.assert_called_once()
        self.client.connection.close.assert_called_once()

    def test_send_pass_success(self):
        self.client.connection = MagicMock()
        self.client.connection.send_request.return_value = None
        self.client.connection.get_response.return_value = {'code': '230'}
        result = self.client._send_pass('password')
        self.assertTrue(result)
        self.assertTrue(self.client.logged_in)
        self.client.connection.send_request.assert_called_with('PASS password')
        self.client.connection.get_response.assert_called_once()

    def test_send_pass_failure(self):
        self.client.connection = MagicMock()
        self.client.connection.send_request.return_value = None
        self.client.connection.get_response.return_value = {'code': '530'}
        result = self.client._send_pass('password')
        self.assertFalse(result)
        self.assertFalse(self.client.logged_in)
        self.client.connection.send_request.assert_called_with('PASS password')
        self.client.connection.get_response.assert_called_once()

    def test_send_pass_invalid(self):
        """
        Tests that the `_send_pass` method returns False if the password is invalid.
        """
        with patch('ftp_client.connect.Connection.send_request'):
            with patch('ftp_client.connect.Connection.get_response', return_value={'code': '530'}):
                self.assertFalse(self.client._send_pass('invalid_password'))

    def test_nlist(self):
        """
        Tests the `nlist` method of the `FTPClient` class.
        """
        self.client.connection.connected = True
        self.client.logged_in = True
        self.client.connection.create_pasv_con.return_value = MagicMock()
        self.client.connection.get_response.return_value = '226 Transfer complete.\r\n'
        self.client.connection.create_pasv_con().recv.return_value = b'file1.txt\r\nfile2.txt\r\n'

        result = self.client.nlist()
        self.assertEqual(result, ['file1.txt', 'file2.txt'])

    def test_list(self):
        """
        Tests the `list` method of the `FTPClient` class.
        """
        self.client.connection.connected = True
        self.client.logged_in = True
        self.client.connection.create_pasv_con.return_value = MagicMock()
        self.client.connection.get_response.return_value = '226 Transfer complete.\r\n'
        self.client.connection.create_pasv_con().recv.return_value = b'file1.txt\r\nfile2.txt\r\n'

        result = self.client.list()
        self.assertEqual(result, ['file1.txt', 'file2.txt'])

    def test_make_directory(self):
        """
        Tests the `make_directory` method of the `FTPClient` class.
        """
        self.client.connection.connected = True
        self.client.logged_in = True
        self.client.connection.get_response.return_value = '257 "/newdir" created.\r\n'

        self.client.make_directory('/newdir')
        self.client.connection.send_request.assert_called_with('MKD /newdir')

    def test_check_connection_connected(self):
        """
        Tests that the `_check_connection` method returns True if the client is connected.
        """
        self.client.connection.connected = True
        self.assertTrue(self.client._check_connection())

    def test_check_logged_in_logged_in(self):
        """
        Tests that the `_check_logged_in` method returns True if the client is logged in.
        """
        self.client.logged_in = True
        self.assertTrue(self.client._check_logged_in())

    def test_make_directory_success(self):
        mock_connection = Mock()
        self.client.connection = mock_connection
        self.client.connection.connected = True
        self.client.logged_in = True
        mock_connection._check_connection.return_value = True
        mock_connection._check_logged_in.return_value = True
        self.client.make_directory('/path/to/directory')
        mock_connection.send_request.assert_called_with('MKD /path/to/directory')
        mock_connection.get_response.assert_called_once()

    def test_upload_file_local_file_not_exist(self):
        local_file = 'path/to/nonexistent/file.txt'
        remote_file = 'path/to/remote/file.txt'
        self.client._check_connection = MagicMock(return_value=True)
        self.client._check_logged_in = MagicMock(return_value=True)
        self.assertFalse(self.client.upload_file(local_file, remote_file))

    def test_download_file_not_found(self):
        remote_file = 'path/to/nonexistent/file.txt'
        local_file = 'path/to/local_directory/file.txt'
        self.client._check_connection = MagicMock(return_value=True)
        self.client._check_logged_in = MagicMock(return_value=True)
        self.client.connection.create_pasv_con = MagicMock()
        self.client.connection.send_request = MagicMock()
        self.client.connection.get_response = MagicMock(return_value={'code': '550'})
        self.client.connection.get_response.return_value = {'code': '550'}
        self.assertFalse(self.client.download_file(remote_file, local_file))

    def test_download_directory_file_list_single_file(self):
        remote_dir = '/path/to/remote/file.txt'
        local_dir = '/path/to/local/directory'
        self.client._check_connection = MagicMock(return_value=True)
        self.client._check_logged_in = MagicMock(return_value=True)
        self.client.list = MagicMock(
            return_value=['-rw-r--r--  1 user group      1234 May 20 15:43 file.txt'])
        self.client.download_directory = MagicMock()
        self.client.download_file = MagicMock()
        self.client.download(remote_dir, local_dir)
        self.assertEqual(self.client.list.call_count, 1)
        self.assertEqual(self.client.download_directory.call_count, 0)
        self.assertEqual(self.client.download_file.call_count, 1)

    def test_download_file_success(self):
        remote_file = 'path/to/remote_file'
        local_file = 'path/to/local_file'
        self.client._check_connection = MagicMock(return_value=True)
        self.client._check_logged_in = MagicMock(return_value=True)
        self.client.connection.server.timeout = MagicMock()
        self.client.connection.create_pasv_con = MagicMock(return_value=MagicMock(bytearray))
        self.client.connection.send_request = MagicMock()
        self.client.connection.get_response = MagicMock()
        self.client.connection.get_response.return_value = {'code': '200'}
        self.client.download_file(remote_file, local_file)
        self.assertEqual(self.client.connection.server.settimeout.call_count, 1)
        self.assertEqual(self.client.connection.create_pasv_con.call_count, 1)

    def test_check_connection_disconnected(self):
        self.client.connection.connected = False
        with patch('builtins.print') as mock_print, self.assertRaises(SystemExit) as cm:
            self.client._check_connection()

        self.assertEqual(cm.exception.code, None)
        mock_print.assert_called_once_with("You are not currently connected to a server.")


if __name__ == '__main__':
    unittest.main()
