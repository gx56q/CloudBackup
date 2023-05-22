import click
from ftp_client.ftpclient import FtpClient
from yadisk_client.yadiskclient_webdav import YaDiskClient


@click.command()
@click.option('-c', '--client', type=click.Choice(['ftp', 'yadisk']), required=True, help='Type of client to use.')
@click.option('--host', type=str, metavar='HOST', help='FTP host.')
@click.option('-u', '--user', type=str, metavar='USERNAME', help='Username.')
@click.option('-p', '--pass', 'password', type=str, metavar='PASSWORD', help='Password.')
@click.option('-t', '--token', type=str, metavar='TOKEN', help='OAuth token.')
@click.option('-d', '--download', nargs=2, type=str, metavar=('REMOTE_PATH', 'LOCAL_PATH'),
              help='Download a file from the remote path to the local path.')
@click.option('-up', '--upload', nargs=2, type=str, metavar=('LOCAL_PATH', 'REMOTE_PATH'),
              help='Upload a file from the local path to the remote path.')
@click.option('-l', '--list', 'list_files', type=str, metavar='REMOTE_PATH', help='List files at the remote path.')
def cli(client, host, user, password, token, download, upload, list_files):
    if client == 'ftp':
        if not host or not user or not password:
            raise click.UsageError('For FTP client, --host, --user, and --pass are required.')
        ftp = FtpClient()
        ftp.connect(host, user, password)
        if download:
            remote_path, local_path = download
            ftp.download(remote_path, local_path)
        if upload:
            local_path, remote_path = upload
            ftp.upload(local_path, remote_path)
        if list_files:
            remote_path = list_files
            ftp.list(remote_path, True)
        ftp.close()

    elif client == 'yadisk':
        yadisk = YaDiskClient()
        if token:
            yadisk.set_token(token)
        elif user and password:
            yadisk.set_auth(user, password)
        else:
            raise click.UsageError('For Yandex Disk client, --user and --pass or --token are '
                                   'required.')
        if download:
            remote_path, local_path = download
            yadisk.download(remote_path, local_path)
            click.echo(f"Yandex Disk: Downloaded {remote_path} to {local_path}")
        if upload:
            local_path, remote_path = upload
            yadisk.upload(local_path, remote_path)
            click.echo(f"Yandex Disk: Uploaded {local_path} to {remote_path}")
        if list_files:
            directory = list_files
            yadisk.list_directory_recursive(directory)
            click.echo(f"Yandex Disk: Listing files at {directory}")


if __name__ == '__main__':
    cli()

