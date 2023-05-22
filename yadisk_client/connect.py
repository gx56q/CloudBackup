from requests import request


class Connection:
    URL = 'https://webdav.yandex.ru/'
    PORT = 443

    def __init__(self):
        self.token = None
        self.username = None
        self.password = None

    def send_request(self, command, add_url="/", add_headers=None, data=None):
        if self.token is None and (self.username is None or self.password is None):
            raise Exception("No token or login/password provided")
        if add_headers is None:
            add_headers = {}
        headers = {"Accept": "*/*"}
        auth = None
        if self.token is not None:
            headers["Authorization"] = "OAuth %s".format(self.token)
        else:
            auth = (self.username, self.password)
        headers.update(add_headers)
        url = self.URL + add_url
        return request(command, url, headers=headers, auth=auth, data=data)
