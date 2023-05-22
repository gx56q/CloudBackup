"""
YaDisk Connection module.

This module contains the Connection class that handles the connection to the Yandex.Disk API.
"""

import requests
from yadisk_client.yadisk_exception import YaDiskException


class Connection:
    """Handles the connection to Yandex.Disk API."""

    URL = 'https://webdav.yandex.ru/'
    PORT = 443

    def __init__(self):
        self.token = None
        self.username = None
        self.password = None

    def send_request(self, command, add_url="/", add_headers=None, data=None):
        """
        Send an HTTP request to Yandex.Disk API.

        Args:
            command (str): The HTTP command to send (e.g., GET, POST, PROPFIND).
            add_url (str): Additional URL path to append to the base URL.
            add_headers (dict): Additional headers to include in the request.
            data: Optional data to include in the request body.

        Returns:
            requests.Response: The response from the API.

        Raises:
            YaDiskException: If token or login/password is not specified.
        """
        if self.token is None and (self.username is None or self.password is None):
            raise YaDiskException(400, "Specify token or login/password for Yandex.Disk account.")

        if add_headers is None:
            add_headers = {}

        headers = {"Accept": "*/*"}
        auth = None

        if self.token is not None:
            headers["Authorization"] = f"OAuth {self.token}"
        else:
            auth = (self.username, self.password)

        headers.update(add_headers)
        url = self.URL + add_url
        return requests.request(command, url, headers=headers, auth=auth, data=data)
