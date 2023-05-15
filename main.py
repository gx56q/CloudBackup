import os
from dotenv import load_dotenv, find_dotenv
import asyncio
import argparse

from ftp_client.ftpclient import FtpClient
from yadisk_client.yadiskclient_webdav import YaDiskClient


async def main():
    parser = argparse.ArgumentParser(description="FTP client")
    parser.add_argument("host", help="FTP server hostname")
    parser.add_argument("-t", "--type", choices=["ftp", "yadisk"], default="ftp", help="Client type")
    parser.add_argument("-p", "--port", type=int, default=21, help="FTP server port")
    parser.add_argument("-u", "--username", required=True, help="FTP server username")
    parser.add_argument("-pw", "--password", required=True, help="FTP server password")
    parser.add_argument("-d", "--download", nargs=2, metavar=("REMOTE_PATH", "LOCAL_PATH"), help="Download file or directory from the FTP server")
    parser.add_argument("-up", "--upload", nargs=2, metavar=("LOCAL_PATH", "REMOTE_PATH"), help="Upload file or directory to the FTP server")
    parser.add_argument("-l", "--list", metavar="REMOTE_PATH", help="List files in the given directory on the FTP server")
    args = parser.parse_args()
    if args.type == "ftp":
        ftp = FtpClient()
        ftp.connect(args.host, args.username, args.password)
        print(f"Connected to {args.host}")
        if args.download:
            remote_path, local_path = args.download
            ftp.download(remote_path, local_path)
            print(f"Downloaded {remote_path} to {local_path}")
        elif args.upload:
            local_path, remote_path = args.upload
            ftp.upload(local_path, remote_path)
            print(f"Uploaded {local_path} to {remote_path}")
        elif args.list:
            remote_path = args.list
            files = ftp.list(remote_path, True)
        ftp.close()
    elif args.type == "yadisk":
        pass

if __name__ == '__main__':
    asyncio.run(main())
    # ftp = FtpClient()
    # ftp.connect(host, username, password)
    # ftp.download('9833-E243/test/', '/local/dir')
    # ftp.upload('/local/dir/remote_file.txt', '9833-E243/test/remote_file.txt')
    # ftp.list('9833-E243/test', True)
    # ftp.close()
    # Загрузка переменных окружения из файла config.env
    load_dotenv(find_dotenv('config.env'))
    YA_TOKEN = os.getenv('YADISK_TOKEN')
    YA_LOGIN = os.getenv('YADISK_USER')
    YA_PASSWORD = os.getenv('YADISK_PASS')
    FTP_HOST = os.getenv('FTP_HOST')
    FTP_USER = os.getenv('FTP_USER')
    FTP_PASS = os.getenv('FTP_PASS')

