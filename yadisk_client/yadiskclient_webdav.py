import os
import xml.etree.ElementTree as Et
from yadisk_client.connect import Connection
from yadisk_client.yadisk_exception import YaDiskException


class YaDiskClient:
    """
    Client for Yandex Disk
    """
    URL = 'https://webdav.yandex.ru/'
    PORT = 443

    def __init__(self):
        self.connection = Connection()
        self.namespaces = {'d': 'DAV:'}

    def set_token(self, token):
        self.connection.token = token
        self.connection.username = None
        self.connection.password = None

    def set_auth(self, login, password):
        self.connection.token = None
        self.connection.username = login
        self.connection.password = password

    def upload_file(self, local_file, remote_file):
        """Upload file."""
        local_file = os.path.abspath(local_file)
        if not os.path.exists(local_file):
            raise FileNotFoundError(f'File {local_file} not found')
        with open(local_file, "rb") as file:
            resp = self.connection.send_request("PUT", remote_file, data=file)
            print(resp.status_code)
            if resp.status_code != 201:
                raise YaDiskException(resp.status_code, resp.content)

    def download_file(self, remote_file, local_file):
        """Download remote file to disk."""
        local_file = os.path.abspath(local_file)
        directory = os.path.dirname(local_file)
        if not os.path.exists(directory):
            os.makedirs(directory)
        resp = self.connection.send_request("GET", remote_file)
        if resp.status_code == 200:
            with open(local_file, "wb") as file:
                file.write(resp.content)
        else:
            raise YaDiskException(resp.status_code, resp.content)

    def download_directory(self, remote_directory, local_directory):
        """Download remote directory to disk."""
        remote_directory = '/' + remote_directory.strip("/") + "/"
        local_directory = os.path.abspath(local_directory)
        if not os.path.exists(local_directory):
            os.makedirs(local_directory)
        directory_contents = self.list_directory(remote_directory)
        for file in directory_contents:
            if file['path'] == remote_directory:
                continue
            if file['isDir']:
                self.download_directory(file['path'], local_directory + os.sep +
                                        file['displayname'])
            else:
                self.download_file(file['path'], local_directory + os.sep + file['displayname'])

    def download(self, remote_path, local_path):
        """Download file or directory."""
        if not remote_path.startswith("/"):
            remote_path = "/" + remote_path
        if not remote_path.endswith("/"):
            remote_path += "/"
        directory_contents = self.list_directory(remote_path)
        if len(directory_contents) == 1 and not directory_contents[0]['isDir']:
            local_path = os.path.abspath(local_path) + os.sep + directory_contents[0]['displayname']
            self.download_file(remote_path, local_path)
        else:
            local_path = os.path.abspath(local_path) + os.sep + \
                         remote_path.strip("/").split("/")[-1]
            self.download_directory(remote_path, local_path)

    def list_directory(self, remote_path):
        """List files in remote path."""
        if not remote_path.startswith("/"):
            remote_path = "/" + remote_path
        if not remote_path.endswith("/"):
            remote_path += "/"
        resp = self.connection.send_request("PROPFIND", remote_path, add_headers={"Depth": "1"})
        if resp.status_code == 207:
            res = self.parse_list(resp.content)
            return res
        raise YaDiskException(resp.status_code, resp.content)

    def list_directory_recursive(self, remote_path):
        """List all files and directories in remote path recursively."""
        if not remote_path.startswith("/"):
            remote_path = "/" + remote_path
        if not remote_path.endswith("/"):
            remote_path += "/"

        def process_directory(directory_path, indent=""):
            directory_contents = self.list_directory(directory_path)
            contents = []
            for file in directory_contents:
                if file['isDir'] and file['path'] != directory_path:
                    contents.extend(process_directory(file['path'], indent + "\t"))
                else:
                    contents.append((file, indent))
            return contents

        base_contents = process_directory(remote_path)

        def format_listing(listing, indent):
            if listing['isDir']:
                return f"{indent}{listing['displayname'] + os.sep}"
            return "{}{} ({} bytes)" \
                .format(indent + "\t", listing['displayname'], listing['length'])

        for item, offset in base_contents:
            print(format_listing(item, offset))
        base_contents = [item for item, offset in base_contents]
        return base_contents

    def parse_list(self, xml):
        result = []
        root = Et.fromstring(xml)
        for response in root.findall('.//d:response', namespaces=self.namespaces):
            node = {
                'path': response.find("d:href", namespaces=self.namespaces).text,
                'creationdate': response.find("d:propstat/d:prop/d:creationdate",
                                              namespaces=self.namespaces).text,
                'displayname': response.find("d:propstat/d:prop/d:displayname",
                                             namespaces=self.namespaces).text,
                'lastmodified': response.find("d:propstat/d:prop/d:getlastmodified",
                                              namespaces=self.namespaces).text,
                'isDir': response.find("d:propstat/d:prop/d:resourcetype/d:collection",
                                       namespaces=self.namespaces) is not None
            }
            if not node['isDir']:
                node['length'] = response.find("d:propstat/d:prop/d:getcontentlength",
                                               namespaces=self.namespaces).text
                node['etag'] = response.find("d:propstat/d:prop/d:getetag",
                                             namespaces=self.namespaces).text
                node['type'] = response.find("d:propstat/d:prop/d:getcontenttype",
                                             namespaces=self.namespaces).text
            result.append(node)
        return result

    def make_directory(self, remote_directory):
        """Make remote directory."""
        resp = self.connection.send_request("MKCOL", remote_directory)
        if resp.status_code != 201:
            raise YaDiskException(resp.status_code, resp.content)
