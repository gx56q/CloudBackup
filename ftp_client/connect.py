"""
FTP Connection module.

This module provides a Connection class for FTP client.
"""

import socket


class Connection:
    """
    Represents a connection to an FTP server.
    """

    PORT = 21

    def __init__(self):
        """
        Initializes the FTP connection.
        """
        self.host = None
        self.server = None
        self.connected = False

    def connect(self, host):
        """
        Connects to the FTP server.

        :arg: host: The hostname or IP address of the FTP server.

        :returns: The response code if successful, or False if the connection fails.
        """
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.host = socket.gethostbyname(host)
        except socket.gaierror:
            return False
        try:
            self.server.connect((self.host, self.PORT))
        except socket.error:
            return False
        self.server.settimeout(20)
        response = self.get_response()
        if not response:
            return False
        self.connected = True
        return response['code']

    def close(self):
        """
        Closes connection to server
        """
        self.server.close()
        self.connected = False

    def send_request(self, request):
        """
        Sends request to server
        """
        request = request.strip()
        self.server.sendall(f'{request}\r\n'.encode())

    def get_response(self, print_response=False):
        """
        Receives response from server, prints and returns the parsed result
        """
        try:
            response = self.server.recv(1024).decode()
            if print_response:
                print(response)
            return self._parse_response(response)
        except socket.timeout:
            print("Timeout error, connection closed")
            self.close()
            exit()

    @staticmethod
    def _parse_response(response):
        """
        Returns a dictionary with the 3 digit response code and message
        """
        response = response.strip().split('\r\n')[-1]
        code = response[:3]
        message = response[4:].strip()
        error = False
        if code[0] == '4' or code[0] == '5':
            error = True
        return {
            'code': code,
            'message': message,
            'error': error
        }

    def create_pasv_con(self):
        """
        Given a response from an issued PASV command, creates a connection
        to the specified host and port.
        """
        self.send_request('PASV')
        response = self.get_response()
        if not response:
            return False
        params = response['message'].split('(')[1].split(')')[0].split(',')
        file_port = (int(params[4]) * 256) + int(params[5])
        file_con = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        file_con.connect((self.host, file_port))
        return file_con
