import unittest
from unittest.mock import patch
from click.testing import CliRunner
from ftp_client.ftpclient import FtpClient
from webdav_api_client.webdav_client import WebDavClient
from main import cli


class TestCli(unittest.TestCase):
    """
    This class contains unit tests for the `cli` function.
    """

    def setUp(self):
        self.runner = CliRunner()

    def test_missing_required_options(self):
        """
        Tests that a `UsageError` is raised if required options are missing.
        """
        result = self.runner.invoke(cli, ['--client_type', 'ftp'])
        self.assertEqual(result.exit_code, 2)
        self.assertIn('--host', result.output)
        self.assertIn('--user', result.output)
        self.assertIn('--pass', result.output)

        result = self.runner.invoke(cli, ['--client_type', 'yadisk'])
        self.assertEqual(result.exit_code, 2)
        self.assertIn('--user', result.output)
        self.assertIn('--pass', result.output)
        self.assertIn('--token', result.output)

        result = self.runner.invoke(cli, ['--client_type', 'cloud_mail'])
        self.assertEqual(result.exit_code, 2)
        self.assertIn('--user', result.output)
        self.assertIn('--pass', result.output)
        self.assertIn('--token', result.output)

    @patch.object(FtpClient, 'connect')
    @patch.object(FtpClient, 'download')
    @patch.object(FtpClient, 'upload')
    @patch.object(FtpClient, 'list')
    @patch.object(FtpClient, 'close')
    def test_ftp_client(self, mock_close, mock_list, mock_upload, mock_download, mock_connect):
        """
        Tests the FTP client functionality.
        """
        result = self.runner.invoke(cli, ['--client_type', 'ftp', '--host', 'example.com', '--user',
                                          'user', '--pass', 'password', '--download', 'remote_path',
                                          'local_path', '--upload', 'local_path', 'remote_path',
                                          '--list', 'remote_path'])
        self.assertEqual(result.exit_code, 0)
        mock_connect.assert_called_once_with('example.com', 'user', 'password')
        mock_download.assert_called_once_with('remote_path', 'local_path')
        mock_upload.assert_called_once_with('local_path', 'remote_path')
        mock_list.assert_called_once_with('remote_path', True, True)
        mock_close.assert_called_once()

    @patch.object(WebDavClient, 'set_token')
    @patch.object(WebDavClient, 'set_auth')
    @patch.object(WebDavClient, 'download')
    @patch.object(WebDavClient, 'upload')
    @patch.object(WebDavClient, 'list_directory_recursive')
    def test_webdav_client(self, mock_list, mock_upload, mock_download, mock_auth, mock_token):
        """
        Tests the WebDav client functionality.
        """
        result = self.runner.invoke(cli,
                                    ['--client_type', 'yadisk', '--token', 'token', '--download',
                                     'remote_path', 'local_path', '--upload', 'local_path',
                                     'remote_path', '--list', 'directory'])
        self.assertEqual(result.exit_code, 0)
        mock_token.assert_called_once_with('token')
        mock_download.assert_called_once_with('remote_path', 'local_path')
        mock_upload.assert_called_once_with('local_path', 'remote_path')
        mock_list.assert_called_once_with('directory')

        result = self.runner.invoke(cli, ['--client_type', 'cloud_mail', '--user', 'user', '--pass',
                                          'password', '--download', 'remote_path', 'local_path',
                                          '--upload', 'local_path', 'remote_path', '--list',
                                          'directory'])
        self.assertEqual(result.exit_code, 0)
        mock_auth.assert_called_once_with('user', 'password')

    def test_invalid_client_type(self):
        """
        Tests that a `UsageError` is raised if an invalid client type is provided.
        """
        result = self.runner.invoke(cli, ['--client_type', 'invalid'])
        self.assertEqual(result.exit_code, 2)
        self.assertIn('Invalid value', result.output)

    def test_cli_runs(self):
        """
        Tests that the CLI runs without errors.
        """
        try:
            # Run the CLI from the main.py file,  note that main.py is in the root directory and not in the tests directory
            exec(open('C:\\Users\\andre\\PycharmProjects\\CloudBackup\\main.py').read())
        except Exception as e:
            self.fail(f"CLI failed to run with error: {e}")


if __name__ == '__main__':
    unittest.main()
