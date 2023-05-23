"""
WebDav Connection module.

This module contains the Connection class that handles the connection to the WebDav API.
"""

import requests
from webdav_api_client.webdav_exception import WebDavException


class Connection:
    """Handles the connection to WebDav API."""

    YADISK_URL = 'https://webdav.yandex.ru/'
    CLOUD_MAIL_URL = 'https://webdav.cloud.mail.ru'
    PORT = 443

    def __init__(self, cloud_type='yadisk'):
        self.token = None
        self.username = None
        self.password = None
        if cloud_type == 'yadisk':
            self.URL = self.YADISK_URL
        elif cloud_type == 'cloud_mail':
            self.URL = self.CLOUD_MAIL_URL

    def send_request(self, command, add_url="/", add_headers=None, data=None):
        """
        Send an HTTP request to WebDav API.

        Args:
            command (str): The HTTP command to send (e.g., GET, POST, PROPFIND).
            add_url (str): Additional URL path to append to the base URL.
            add_headers (dict): Additional headers to include in the request.
            data: Optional data to include in the request body.

        Returns:
            requests.Response: The response from the API.

        Raises:
            WebDavException: If token or login/password is not specified.
        """
        if self.token is None and (self.username is None or self.password is None):
            raise WebDavException(400,
                                  "Specify token or login/password for WebDav storage account.")

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
