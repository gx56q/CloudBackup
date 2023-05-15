import os
import requests
import aiohttp
import asyncio


class YaDiskClient:
    """
    Класс для работы с API Яндекс.Диска
    """

    URL = 'https://cloud-api.yandex.net/v1/disk/resources'
    TOKEN = None
    headers = None

    def __init__(self, token):
        self.TOKEN = token
        self.headers = {'Content-Type': 'application/json', 'Accept': 'application/json',
                        'Authorization': f'OAuth {token}'}

    def mkdir(self, directory):
        """
        Sends a request to create a directory on the server.

        :param directory: The name of the directory to create.

        :return: True if the directory was created successfully, False otherwise.
        """
        res = requests.put(f'{self.URL}?path={directory}', headers=self.headers)
        if res.status_code == 201:
            return True
        else:
            print(res)
            return False

    async def upload_file(self, local_file: str, remote_file: str, replace: bool) -> bool:
        """
        Uploads a local file to the server.

        :param local_file: Path to the local file.
        :param remote_file: Path to the remote file.
        :param replace: Whether to replace the file if it already exists.

        :return: True if the file was uploaded successfully, False otherwise
        """
        res = requests.get(f'{self.URL}/upload?path={remote_file}&overwrite={replace}', headers=self.headers).json()
        with open(local_file, 'rb') as f:
            if res.get("href"):
                requests.put(res['href'], files={'file': f})
                return True
            else:
                print(res)
                return False

    async def upload_directory(self, local_dir: str, remote_dir: str) -> None:
        """
        Uploads a directory to the server

        :param local_dir: local directory to upload
        :param remote_dir: remote directory to upload to
        :return: None
        """
        '''self.mkdir(save_path)
        for address, dirs, files in os.walk(load_path):
            parent = address.replace("\\", "/")
            self.create_folder('{0}/{1}'.format(save_path, parent))
            for file in files:
                self.upload_file('{0}/{1}'.format(address, file),
                                 '{0}/{1}/{2}'.format(save_path, parent, file))'''
        loop = asyncio.get_event_loop()
        tasks = [self.upload_file('{0}/{1}'.format(address, file),
                                  '{0}/{1}/{2}'.format(remote_dir, address.replace("\\", "/"), file))
                 for address, dirs, files in os.walk(local_dir) for file in files]
        loop.run_until_complete(asyncio.wait(tasks))

    def get_files_list(self, directory):
        """
        Sends a request to receive the contents of a directory on the server.

        :param directory: The name of the directory to list .

        :return: A list of strings representing the contents of the directory.
        """
        res = requests.get(f'{self.URL}?path={directory}', headers=self.headers).json()
        if res.get('_embedded'):
            return res['_embedded']['items']
        else:
            return [res]

    def download_file(self, remote_file, local_file):
        """
        Downloads a single file from the remote server to the local machine.

        :param remote_file: file to download from the server
        :param local_file: file to save on the local machine
        :return: None
        """
        res = requests.get(f'{self.URL}/download?path={remote_file}', headers=self.headers)
        if res.status_code == 200:
            if not os.path.exists(local_file):
                os.makedirs(local_file)
            link = res.json()['href']
            file_name = link.split('/')[-1].split('&')[1].split('=')[1]
            with open('{0}/{1}'.format(local_file, file_name), 'wb') as f:
                f.write(requests.get(link).content)
                return '{0}/{1}'.format(local_file, file_name)
        else:
            print(res)

    def download_directory(self, remote_dir, local_dir):
        """
        Downloads a whole directory recursively from the remote server to the local machine.

        :param remote_dir: directory to download from the server
        :param local_dir: directory to save files on the local machine
        :return: None
        """
        files = self.get_files_list(remote_dir)
        if not os.path.exists(local_dir):
            os.makedirs(local_dir)
        '''for file in files:
            if file['type'] == 'dir':
                self.download_from_disk(file['path'], local_dir+'/'+file['name'])
            else:
                self.download_file(file['path'], local_dir)'''
        loop = asyncio.get_event_loop()
        tasks = [self.download_file(file['path'], local_dir) for file in files if file['type'] == 'file']
        loop.run_until_complete(asyncio.wait(tasks))