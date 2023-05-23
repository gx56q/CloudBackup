import click

from ftp_client.ftpclient import FtpClient
from webdav_api_client.webdav_client import WebDavClient


@click.command()
@click.option('-c', '--client_type', type=click.Choice(['ftp', 'yadisk', 'cloud_mail']),
              required=True, help='Client''to use.')
@click.option('--host', type=str, metavar='HOST', help='FTP host.')
@click.option('-u', '--user', type=str, metavar='USERNAME', help='Username.')
@click.option('-p', '--pass', 'password', type=str, metavar='PASSWORD', help='Password.')
@click.option('-t', '--token', type=str, metavar='TOKEN', help='OAuth token.')
@click.option('-d', '--download', nargs=2, type=str, metavar=('REMOTE_PATH', 'LOCAL_PATH'),
              help='Download a file from the remote path to the local path.')
@click.option('-up', '--upload', nargs=2, type=str, metavar=('LOCAL_PATH', 'REMOTE_PATH'),
              help='Upload a file from the local path to the remote path.')
@click.option('-l', '--list', 'list_files', type=str, metavar='REMOTE_PATH', help='List files at '
                                                                                  'the remote '
                                                                                  'path.')
def cli(client_type, host, user, password, token, download, upload, list_files):
    if client_type == 'ftp':
        if not host or not user or not password:
            raise click.UsageError('For FTP client, --host, --user, and --pass are required.')
        ftp_client = FtpClient()
        ftp_client.connect(host, user, password)
        if download:
            remote_path, local_path = download
            ftp_client.download(remote_path, local_path)
        if upload:
            local_path, remote_path = upload
            ftp_client.upload(local_path, remote_path)
        if list_files:
            remote_path = list_files
            ftp_client.list(remote_path, True)
        ftp_client.close()
    elif client_type == 'yadisk' or client_type == 'cloud_mail':
        if client_type == 'cloud_mail':
            webdav_client = WebDavClient('cloud_mail')
        else:
            webdav_client = WebDavClient('yadisk')
        if token:
            webdav_client.set_token(token)
        elif user and password:
            webdav_client.set_auth(user, password)
        else:
            raise click.UsageError('For WebDav client, --user and --pass or --token are '
                                   'required.')
        if download:
            remote_path, local_path = download
            webdav_client.download(remote_path, local_path)
        if upload:
            local_path, remote_path = upload
            webdav_client.upload(local_path, remote_path)
        if list_files:
            directory = list_files
            webdav_client.list_directory_recursive(directory)
    else:
        raise click.UsageError('Invalid client type.')


if __name__ == '__main__':
    cli()
