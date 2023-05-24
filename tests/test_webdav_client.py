import os
import unittest
from unittest.mock import MagicMock, patch

from dotenv import load_dotenv, find_dotenv
from webdav_api_client.webdav_client import WebDavClient


class TestWebdavClient(unittest.TestCase):
    def setUp(self):
        load_dotenv(find_dotenv('config.env'))
        self.client = WebDavClient()

    def test_set_token(self):
        token = "your_token"
        self.client.connection = MagicMock()

        self.client.set_token(token)

        self.assertEqual(self.client.connection.token, token)
        self.assertIsNone(self.client.connection.username)
        self.assertIsNone(self.client.connection.password)

    def test_set_auth(self):
        login = "your_login"
        password = "your_password"
        self.client.connection = MagicMock()

        self.client.set_auth(login, password)

        self.assertIsNone(self.client.connection.token)
        self.assertEqual(self.client.connection.username, login)
        self.assertEqual(self.client.connection.password, password)

    def test_upload_file_success(self):
        local_file = "path/to/local_file"
        remote_file = "path/to/remote_file"
        self.client.connection = MagicMock()
        self.client.connection.send_request.return_value.status_code = 201

        with unittest.mock.patch("builtins.open",
                                 unittest.mock.mock_open(read_data=b"file_content")) as mock_file:
            self.client.upload_file(local_file, remote_file)

        self.client.connection.send_request.assert_called_once_with("PUT", remote_file,
                                                                    data=mock_file.return_value)

    def test_upload_directory(self):
        local_dir = "test_files/local_dir"
        remote_dir = "path/to/remote_dir"
        self.client.make_directory = MagicMock()
        self.client.upload_file = MagicMock()

        self.client.upload_directory(local_dir, remote_dir)

        self.client.make_directory.assert_called_once_with(remote_dir)

    def test_download_file_success(self):
        remote_file = "path/to/remote_file"
        local_file = "path/to/local_file"
        self.client.connection = MagicMock()
        self.client.connection.send_request.return_value.status_code = 200
        self.client.connection.send_request.return_value.content = b"file_content"

        self.client.download_file(remote_file, local_file)

        self.client.connection.send_request.assert_called_once_with("GET", remote_file)

        with open(local_file, "rb") as file:
            self.assertEqual(file.read(), b"file_content")

    def test_upload_with_existing_local_dir(self):
        with patch.object(self.client, 'make_directory') as mock_make_dir, \
                patch.object(self.client, 'upload_directory') as mock_upload_dir:
            with self.assertRaises(SystemExit):
                self.client.upload('path/to/local_dir', 'path/to/remote_dir')
            mock_make_dir.assert_not_called()
            mock_upload_dir.assert_not_called()

    def test_upload_with_non_existing_local_dir(self):
        with patch.object(self.client, 'make_directory') as mock_make_dir, \
                patch.object(self.client, 'upload_file') as mock_upload_file:
            with patch('os.path.exists', return_value=False):
                with self.assertRaises(SystemExit):
                    self.client.upload('non_existing_dir', 'path/to/remote_dir')
                mock_make_dir.assert_not_called()
                mock_upload_file.assert_not_called()

    def test_upload_with_existing_local_file(self):
        with patch.object(self.client, 'make_directory') as mock_make_dir, \
                patch.object(self.client, 'upload_file') as mock_upload_file:
            self.client.upload('path/to/local_file', 'path/to/remote_dir')
            self.assertEqual(mock_make_dir.call_count, 3)
            mock_upload_file.assert_called_once_with(os.path.abspath('path/to/local_file'),
                                                     '/path/to/remote_dir/local_file/local_file')

    def test_download_directory_with_existing_remote_directory(self):
        with patch('os.path.exists', return_value=False), \
                patch('os.makedirs'):
            with patch.object(self.client, 'list_directory') as mock_list_dir, \
                    patch.object(self.client, 'download_directory') as mock_download_dir, \
                    patch.object(self.client, 'download_file'):
                mock_list_dir.return_value = [
                    {'path': '/remote_dir/', 'isDir': True, 'displayname': 'subdir1'},
                    {'path': '/remote_dir/subdir1/', 'isDir': False, 'displayname': 'file1.txt'}
                ]
                self.client.download_directory('/remote_dir/', 'path/to/local_dir')
                mock_download_dir.assert_called_once_with('/remote_dir/', 'path/to/local_dir')

    def test_download_directory_with_non_existing_remote_directory(self):
        with patch('os.path.exists', return_value=False), \
                patch('os.makedirs'):
            with patch.object(self.client, 'list_directory') as mock_list_dir, \
                    patch.object(self.client, 'download_directory') as mock_download_dir, \
                    patch.object(self.client, 'download_file') as mock_download_file:
                mock_list_dir.return_value = []
                self.client.download_directory('/non_existing_remote_dir/', 'path/to/local_dir')
                mock_download_dir.assert_called_once()
                mock_download_file.assert_not_called()

    def test_download_directory(self):
        remote_directory = "/path/to/remote_directory"
        local_directory = "path/to/local_directory"
        self.client.list_directory = MagicMock(return_value=[
            {'path': '/path/to/remote_directory/', 'displayname': 'file1.txt', 'isDir': False},
            {'path': '/path/to/remote_directory/subdir/', 'displayname': 'file2.txt',
             'isDir': False},
            {'path': '/path/to/remote_directory/subdir/subsubdir/', 'displayname': 'file3.txt',
             'isDir': False},
            {'path': '/path/to/remote_directory/subdir/subsubdir/', 'displayname': 'subsubsubdir',
             'isDir': True},
        ])
        self.client.download_file = MagicMock()
        self.client.download_directory = MagicMock()
        self.client.download_directory(remote_directory, local_directory)

    def test_download_single_file(self):
        remote_path = "/path/to/remote_file/"
        local_path = "path/to/local_file/"
        self.client.list_directory = MagicMock(return_value=[
            {'path': '/path/to/remote_file/', 'displayname': 'file.txt', 'isDir': False},
        ])
        self.client.download_file = MagicMock()
        self.client.download(remote_path, local_path)
        self.client.download_file.assert_called_once_with('/path/to/remote_file/',
                                                          os.path.abspath(os.path.join(local_path,
                                                                                       'file.txt')))

    def test_list_directory(self):
        remote_path = "/path/to/remote_directory/"
        self.client.connection.send_request = MagicMock()
        self.client.connection.send_request.return_value.status_code = 207
        self.client.parse_list = MagicMock(return_value=[
            {'path': '/path/to/remote_directory/', 'displayname': 'file1.txt', 'isDir': False},
            {'path': '/path/to/remote_directory/subdir/', 'displayname': 'file2.txt',
             'isDir': False},
            {'path': '/path/to/remote_directory/subdir/subsubdir/', 'displayname': 'file3.txt',
             'isDir': False},
            {'path': '/path/to/remote_directory/subdir/subsubdir/', 'displayname': 'subsubsubdir',
             'isDir': True},
        ])

        result = self.client.list_directory(remote_path)

        self.client.connection.send_request.assert_called_once_with("PROPFIND", remote_path,
                                                                    add_headers={"Depth": "1"})
        self.client.parse_list.assert_called_once_with(
            self.client.connection.send_request.return_value.content)
        expected_result = [
            {'path': '/path/to/remote_directory/', 'displayname': 'file1.txt', 'isDir': False},
            {'path': '/path/to/remote_directory/subdir/', 'displayname': 'file2.txt',
             'isDir': False},
            {'path': '/path/to/remote_directory/subdir/subsubdir/', 'displayname': 'file3.txt',
             'isDir': False},
            {'path': '/path/to/remote_directory/subdir/subsubdir/', 'displayname': 'subsubsubdir',
             'isDir': True},
        ]
        self.assertEqual(result, expected_result)

    def test_parse_list(self):
        # Test case for parsing XML response and constructing result list
        xml_response = """
        <d:multistatus xmlns:d="DAV:">
            <d:response>
                <d:href>/path/to/file1</d:href>
                <d:propstat>
                    <d:prop>
                        <d:displayname>file1.txt</d:displayname>
                        <d:getcontentlength>100</d:getcontentlength>
                        <d:getetag>123456</d:getetag>
                        <d:getcontenttype>text/plain</d:getcontenttype>
                    </d:prop>
                </d:propstat>
            </d:response>
            <d:response>
                <d:href>/path/to/directory</d:href>
                <d:propstat>
                    <d:prop>
                        <d:displayname>directory</d:displayname>
                        <d:resourcetype>
                            <d:collection/>
                        </d:resourcetype>
                    </d:prop>
                </d:propstat>
            </d:response>
        </d:multistatus>
        """
        expected_result = [
            {
                'path': '/path/to/file1',
                'displayname': 'file1.txt',
                'isDir': False,
                'length': '100',
                'etag': '123456',
                'type': 'text/plain'
            },
            {
                'path': '/path/to/directory',
                'displayname': 'directory',
                'isDir': True
            }
        ]

        result = self.client.parse_list(xml_response)

        self.assertEqual(result, expected_result)

    def test_make_directory(self):
        remote_directory = "/path/to/remote_dir"
        self.client.connection = MagicMock()
        self.client.connection.send_request.return_value.status_code = 201

        self.client.make_directory(remote_directory)

        self.client.connection.send_request.assert_called_once_with("MKCOL", remote_directory)


if __name__ == '__main__':
    unittest.main()
