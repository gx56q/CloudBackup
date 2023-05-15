import os

from yadisk_client.connect import *


class YaDiskClient:
    """
    Creates new connection object, sets default modes
    """
    URL = 'https://webdav.yandex.ru/'
    PORT = 443

    def __init__(self):
        self.password = None
        self.login = None
        self.token = None
        self.connection = Connection()
        self.current_dir = os.getcwd()
        self.logged_in = False
        # Interaction is on by default (user prompts for actions)

    def set_token(self, token):
        self.token = token
        self.login = None
        self.password = None

    def set_auth(self, login, password):
        self.token = None
        self.login = login
        self.password = password

    def check_token(self):
        self.connection.send_request()
