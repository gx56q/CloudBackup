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

    def create_folder(self, path):
        """Создание папки. \n path: Путь к создаваемой папке."""
        res = requests.put(f'{self.URL}?path={path}', headers=self.headers)
        if res.status_code == 201:
            return True
        else:
            print(res)

    def upload_file(self, loadfile, savefile, replace=True):
        """Загрузка файла.
        savefile: Путь к файлу на Диске \n
        loadfile: Путь к загружаемому файлу \n
        replace: true or false Замена файла на Диске"""
        res = requests.get(f'{self.URL}/upload?path={savefile}&overwrite={replace}', headers=self.headers).json()
        with open(loadfile, 'rb') as f:
            if res.get("href"):
                requests.put(res['href'], files={'file': f})
            else:
                print(res)

    def upload_directory(self, load_path, save_path):
        """Загрузка папки на Диск.
        :param save_path: Путь к папке на Диске для сохранения
        :param load_path: Путь к загружаемой папке"""
        '''self.create_folder(save_path)
        for address, dirs, files in os.walk(load_path):
            parent = address.replace("\\", "/")
            self.create_folder('{0}/{1}'.format(save_path, parent))
            for file in files:
                self.upload_file('{0}/{1}'.format(address, file),
                                 '{0}/{1}/{2}'.format(save_path, parent, file))'''
        loop = asyncio.get_event_loop()
        tasks = [self.upload_file('{0}/{1}'.format(address, file),
                                  '{0}/{1}/{2}'.format(save_path, address.replace("\\", "/"), file))
                 for address, dirs, files in os.walk(load_path) for file in files]
        loop.run_until_complete(asyncio.wait(tasks))

    def get_files_list(self, path):
        """Получение списка файлов в папке
        :param path: Путь к папке на Диске"""
        res = requests.get(f'{self.URL}?path={path}', headers=self.headers).json()
        if res.get('_embedded'):
            return res['_embedded']['items']
        else:
            return [res]

    def download_file(self, loadfile, save_dir):
        """Загрузка файла
        :param savefile: Путь к файлу на Диске
        :param loadfile: Путь к загружаемому файлу"""
        res = requests.get(f'{self.URL}/download?path={loadfile}', headers=self.headers)
        if res.status_code == 200:
            if not os.path.exists(save_dir):
                os.makedirs(save_dir)
            link = res.json()['href']
            file_name = link.split('/')[-1].split('&')[1].split('=')[1]
            with open('{0}/{1}'.format(save_dir, file_name), 'wb') as f:
                f.write(requests.get(link).content)
                return '{0}/{1}'.format(save_dir, file_name)
        else:
            print(res)

    def download_from_disk(self, loadpath, savepath):
        """Загрузка папки с Диска.
        :param savepath: Путь к папке на Диске для сохранения
        :param loadpath: Путь к загружаемой папке"""
        files = self.get_files_list(loadpath)
        if not os.path.exists(savepath):
            os.makedirs(savepath)
        '''for file in files:
            if file['type'] == 'dir':
                self.download_from_disk(file['path'], savepath+'/'+file['name'])
            else:
                self.download_file(file['path'], savepath)'''
        loop = asyncio.get_event_loop()
        tasks = [self.download_file(file['path'], savepath) for file in files if file['type'] == 'file']
        loop.run_until_complete(asyncio.wait(tasks))

    async def get_directory_listing(self, path):
        """Получение списка файлов в папке.
        :param path: str path to directory
        :return: list of files in directory
        """
        res = requests.get(f'{self.URL}?path={path}', headers=self.headers).json()
        if res.get('_embedded'):
            return res['_embedded']['items']
        else:
            return [res]
