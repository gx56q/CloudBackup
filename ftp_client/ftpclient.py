"""
FTP Client module.

This module provides a client for interacting with an FTP server.
"""
import os
import asyncio

from ftp_client.connect import Connection


class FtpClient:
    """
    A client for interacting with an FTP server.

    :ivar connection (Connection): The connection object used for communication with the server.
    :ivar current_dir (str): The current working directory on the server.
    :ivar transfer_type (tuple): A tuple containing the current transfer mode and description.
    :ivar logged_in (bool): Whether the client is logged in to the server.
    """

    def __init__(self):
        """
        Initializes a new FtpClient object with default modes.
        """
        self.connection = Connection()
        self.current_dir = os.getcwd()
        self.transfer_type = ('I', 'binary')
        self.logged_in = False

    def connect(self, host: str, user: str, password: str):
        """
        Connects to the specified FTP server and prompts for authentication.

        :param host: The hostname or IP address of the FTP server.
        :param user: The username to authenticate with.
        :param password: The password to authenticate with.

        :raises ConnectionError: If the connection to the server cannot be established.
        :raises ValueError: If any of the input parameters are invalid.
        """
        if not self.connection.connected:
            connect_code = self.connection.connect(host)
            if connect_code == '220':
                self.connection.send_request('USER ' + user)
                response = self.connection.get_response()
                if response and response['code'] == '331':
                    self.connection.send_request('PASS ' + password)
                    response = self.connection.get_response()
                    if response and response['code'] == '230':
                        self.logged_in = True
                    else:
                        raise ValueError("Login failed.")
                    if self.logged_in:
                        self.connection.send_request('TYPE I')
                        self.connection.get_response()
            else:
                raise ConnectionError("Error: " + host + " is not a valid host.")

    def close(self) -> None:
        """
        Closes the connection to the FTP server.

        :raises ConnectionError: If the connection is not currently open.

        """
        if self._check_connection():
            self.connection.send_request('QUIT')
            self.connection.get_response()
            self.connection.close()
            self.logged_in = False

    def _send_pass(self, password):
        """
        Sends a password to the server for authentication.

        :param password: The password to send to the server.

        :return: True if the password is accepted, False otherwise.
        """
        self.connection.send_request('PASS ' + password)
        response = self.connection.get_response()
        if response and response['code'] == '230':
            self.logged_in = True
            return True
        return False

    def nlist(self, directory=''):
        """
        Sends a request to receive the current working directory's contents.

        :param directory: The name of the directory to list (default is the current directory).

        :return: A list of strings representing the contents of the directory.
        """
        result = []
        if self._check_connection() and self._check_logged_in():
            pasv_con = self.connection.create_pasv_con()
            if not pasv_con:
                return False
            self.connection.send_request('NLST ' + directory)
            self.connection.get_response()
            from_server = pasv_con.recv(4096).decode('utf-8')
            print(from_server)
            result = from_server.strip('\r\n').split('\r\n')
            self.connection.get_response()
            pasv_con.close()
        return result

    def list(self, directory='', list_all=False, print_result=False):
        """
        Sends a request to receive the contents of a directory on the server.

        :param directory: The name of the directory to list (default is the current directory).
        :param list_all: Whether to list directories recursively.
        :param print_result: Whether to print the result to the console.

        :return: A list of strings representing the contents of the directory.

        :raises ConnectionError: If the connection to the server cannot be established.
        """
        result = []
        if self._check_connection() and self._check_logged_in():
            pasv_con = self.connection.create_pasv_con()
            if not pasv_con:
                raise ConnectionError("Error: Could not establish a connection to the server.")
            if list_all:
                self.connection.send_request('LIST -R ' + directory)
            else:
                self.connection.send_request('LIST ' + directory)
            self.connection.get_response()
            from_server = pasv_con.recv(4096).decode('utf-8')
            if print_result:
                print(from_server)
            result = list(filter(None, from_server.strip('\r\n').split('\r\n')))
            self.connection.get_response()
            pasv_con.close()
        return result

    def make_directory(self, directory: str) -> None:
        """
        Sends a request to create a directory on the server.

        :param directory: Path to the directory to create.

        :return: None
        """
        if self._check_connection() and self._check_logged_in():
            self.connection.send_request('MKD ' + directory)
            self.connection.get_response()

    def upload_file(self, local_file: str, remote_file: str) -> bool:
        """
        Uploads a local file to the server.

        :param local_file: Path to the local file.
        :param remote_file: Path to the remote file.

        :return: True if the file was uploaded successfully, False otherwise
        """
        if self._check_connection() and self._check_logged_in():
            if os.path.isfile(local_file):
                self.connection.server.settimeout(120)
                if os.path.dirname(remote_file) != '':
                    self.make_directory(os.path.dirname(remote_file).replace('\\', '/'))
                with open(local_file, 'rb') as to_send:
                    pasv_con = self.connection.create_pasv_con()
                    if not pasv_con:
                        print('Error: Could not establish a connection to the server to upload '
                              f'the file {local_file}.')
                        return False
                    self.connection.send_request('STOR ' + remote_file)
                    self.connection.get_response()
                    response = pasv_con.send(to_send.read())
                    if response == 0:
                        print(f'Error: Could not upload the file {local_file}.')
                        return False
                pasv_con.close()
                self.connection.get_response()
                self.connection.server.settimeout(20)
                return True
            print(f'Error: {local_file} does not exist.')
            return False
        return False

    def upload_directory(self, local_dir: str, remote_dir: str) -> None:
        """
        Uploads a directory to the server

        :param local_dir: local directory to upload
        :param remote_dir: remote directory to upload to
        """
        if self._check_connection() and self._check_logged_in():
            self.make_directory(remote_dir)
            for file_name in os.listdir(local_dir):
                file_path = os.path.join(local_dir, file_name).replace('\\', '/')
                if os.path.isdir(file_path):
                    self.upload_directory(file_path, os.path.join(remote_dir, file_name)
                                          .replace('\\', '/'))
                else:
                    self.upload_file(file_path, os.path.join(remote_dir, file_name)
                                     .replace('\\', '/'))

    def upload(self, local_dir: str, remote_dir: str) -> None:
        """
        Uploads a file or directory to the server

        :param local_dir: local directory to upload
        :param remote_dir: remote directory to upload to
        """
        if self._check_connection() and self._check_logged_in():
            if os.path.isdir(local_dir):
                remote_dir = os.path.join(remote_dir, os.path.basename(local_dir)) \
                    .replace('\\', '/')
                path_to_create = ''
                for sub_dir in remote_dir.split('/'):
                    path_to_create = os.path.join(path_to_create, sub_dir).replace('\\', '/')
                    self.make_directory(path_to_create)
                self.upload_directory(local_dir, remote_dir)
            else:
                self.upload_file(local_dir, remote_dir)

    def download_file(self, remote_file, local_file):
        """
        Downloads a single file from the remote server to the local machine.

        :param remote_file: file to download from the server
        :param local_file: file to save on the local machine
        :return: None
        """
        if self._check_connection() and self._check_logged_in():
            self.connection.server.settimeout(120)
            pasv_con = self.connection.create_pasv_con()
            if not pasv_con:
                print('Error: Could not establish a connection to the server to download the file'
                      f' {remote_file}.')
                return False
            self.connection.send_request('RETR ' + remote_file)
            response = self.connection.get_response()
            if response and response['code'] == '550':
                pasv_con.close()
                print(f'Error: Could not download the file {remote_file}.'
                      ' File does not exist on the server.')
                return False
            with open(local_file, 'wb') as file:
                while True:
                    recv_data = pasv_con.recv(1024)
                    if not recv_data:
                        break
                    file.write(recv_data)
            response = self.connection.get_response()
            if response and response['code'] == '550':
                pasv_con.close()
                print(f'Error: Could not download the file {remote_file}.')
                return False
            pasv_con.close()
            self.connection.server.settimeout(20)
            return True
        return False

    async def download_directory(self, remote_dir, local_dir):
        """
        Downloads a whole directory recursively from the remote server to the local machine.

        :param remote_dir: directory to download from the server
        :param local_dir: directory to save files on the local machine
        :return: None
        """
        if not os.path.exists(local_dir):
            os.makedirs(local_dir)
        files = self.list(remote_dir, False, False)
        for line in files:
            fields = line.split()
            name = fields[-1]
            path = os.path.join(remote_dir, name).replace('\\', '/')
            if line.startswith('d'):
                await self.download_directory(path, os.path.join(local_dir, name)
                                              .replace('\\', '/'))
            else:
                local_file_path = os.path.join(local_dir, name).replace('\\', '/')
                await asyncio.get_running_loop().run_in_executor(None, self.download_file, path,
                                                                 local_file_path)

    def download(self, remote_dir: str, local_dir: str) -> None:
        """
        Downloads a file or directory from the remote server to the local machine.

        :param remote_dir: file or directory to download from the server
        :param local_dir: directory to save files on the local machine
        :raises FileNotFoundError: if the remote file or directory does not exist
        """
        if self._check_connection() and self._check_logged_in():
            file_list = self.list(remote_dir, False, False)
            if len(file_list) == 1:
                if file_list[0].startswith('d'):
                    local_dir = os.path.join(local_dir, os.path.basename(remote_dir.strip('/')))
                    asyncio.run(self.download_directory(remote_dir, local_dir))
                else:
                    local_file = os.path.join(local_dir, os.path.basename(remote_dir))
                    self.download_file(remote_dir, local_file)
            elif len(file_list) > 1:
                local_dir = os.path.join(local_dir, os.path.basename(remote_dir.strip('/')))
                asyncio.run(self.download_directory(remote_dir, local_dir))
            else:
                raise FileNotFoundError(f'No such file or directory: {remote_dir}')

    def ascii(self) -> None:
        """
        Sets transfer type to ASCII (for text files).

        :raises ConnectionError: if the transfer type could not be set to ASCII
        """
        if self._check_connection() and self._check_logged_in():
            self.connection.send_request('TYPE A')
            response = self.connection.get_response()
            if not response['error']:
                self.transfer_type = ('A', 'ascii')
            else:
                print(response['message'])
                raise ConnectionError("Could not set transfer type to ASCII.")

    def image(self) -> None:
        """
        Sets transfer type to binary (for image or binary files).

        :raises ConnectionError: if the transfer type could not be set to binary
        """
        if self._check_connection() and self._check_logged_in():
            self.connection.send_request('TYPE I')
            response = self.connection.get_response()
            if not response['error']:
                self.transfer_type = ('I', 'binary')
            else:
                print(response['message'])
                raise ConnectionError("Could not set transfer type to binary.")

    def _check_connection(self) -> bool:
        """
        Checks whether the client is connected to an FTP server

        :return: True if connected
        :raises ConnectionError if not connected
        """
        if self.connection.connected:
            return True
        raise ConnectionError("You are not currently connected to a server.")

    def _check_logged_in(self) -> bool:
        """
        Checks whether the client is logged in to an FTP server

        :return: True if logged in
        :raises ConnectionError if not logged in
        """
        if self.logged_in:
            return True
        raise ConnectionError("You are not logged in.")
