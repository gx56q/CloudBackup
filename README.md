<h1 align="center">Welcome to CloudBackup 👋</h1>
<p>
  <a href="https://github.com/gx56q/CloudBackup/blob/master/LICENSE" target="_blank">
    <img alt="License: MIT license" src="https://img.shields.io/badge/License-MIT license-yellow.svg" />
  </a>
</p>

> Utility for backing up files to remote storage.
> 
> Currently supported: Yandex Disk, Cloud Mail.ru and FTP.

## Installation
To use CloudBackup, follow these steps:

#### 1. Clone the repository:
```sh
git clone https://github.com/gx56q/CloudBackup.git
```
#### 2. Navigate to the project directory:
```sh
cd CloudBackup
```
#### 3. Install the required dependencies using pip:
```sh
pip install -r requirements.txt
```

## Usage

CloudBackup provides a simple and intuitive command-line interface for performing various actions. The general format of the command is as follows:

```sh
python3 main.py -c <client_type> [client_options] <action> [action_arguments]
```

### Client Options
Before specifying an action, you need to choose a client type using the -c or --client_type option. The available client types are:

- ftp: For FTP clients.
- yadisk: For Yandex Disk clients.
- cloud_mail: For Cloud Mail.ru clients.

Depending on the client type chosen, you need to provide the following additional options:

- For ftp client:
    - -h or --host: The FTP host address.
    - -u or --user: The FTP username.
    - -p or --pass: The FTP password.

 
- For yadisk and cloud_mail clients:

    - -u or --user: The username or email.
    - -p or --pass: The password.

### Actions
After specifying the client type and its required options, you can perform actions on the remote storage. The available actions are:

#### Downloading Files
To download a file from the remote path to the local path, use the -d option followed by the remote path and local path. The command format is:

```sh
python3 main.py -c <client_type> [client_options] -d <remote_path> <local_path>
```

Example:

```sh
python3 main.py -c ftp -h 0.0.0.0 -u USERNAME -p PASSWORD -d <remote_path> <local_path>
```
#### Uploading Files
To upload a file from the local path to the remote path, use the -up option followed by the local path and remote path. The command format is:

```sh
python3 main.py -c <client_type> [client_options] -up <local_path> <remote_path>
```
Example:

```sh
python3 main.py -c yadisk -u USERNAME -p PASSWORD -up <local_path> <remote_path>
```
#### Listing Files
To list files at the remote path, use the -l option followed by the remote path. The command format is:

```sh
python3 main.py -c <client_type> [client_options] -l <remote_path>
```
Example:

```sh
python3 main.py -c cloud_mail -u USERNAME -p PASSWORD -l <remote_path>
```

#### Help

To get help on the available options and actions, use the -h or --help option. The command format is:

```sh
python3 main.py --help
```

## Configuring Passwords for Yandex Disk and Cloud Mail.ru
To authenticate and connect to Yandex.Disk and Cloud Mail.ru, you need to provide your username and password. However, you should not use your actual password for security reasons. Instead, you should create an app password for CloudBackup and use it for authentication.

To configure passwords for Yandex Disk and Cloud Mail.ru, follow these steps:

### Yandex Disk Password

Follow these steps to create an app password for Yandex.Disk:

1. Go to the [Yandex.Passport](https://passport.yandex.com/profile) page and log in to your account.

2. Under __Passwords and authorization__, click __Enable app passwords__ Then enter your password to confirm the action. If you have already enabled app passwords, skip this step.

3. Click __Create an app password__.

4. Select the app type __WebDAV files__.

5. Enter a name for the password (for example, "Yandex.Disk WebDAV").

6. 	Click __Create__.

Use the new app password for authorization in CloudBackup.

### Cloud Mail.ru Password

Follow these steps to create an app password for Cloud Mail.ru:

1. Go to settings [Mail ID](https://id.mail.ru/) → «[Security](https://id.mail.ru/security)» → «[Passwords for external applications](https://account.mail.ru/user/2-step-auth/passwords/)».
2. Click __Add__
3. Enter a name for the password (for example, "Cloud Mail.ru WebDAV").
4. Click __Continue__.

Use the new app password for authorization in CloudBackup.

## Author

👤 **Voinov Andrey**

* Github: [@gx56q](https://github.com/gx56q)

## 🤝 Contributing

Contributions, issues and feature requests are welcome!<br />Feel free to check [issues page](https://github.com/gx56q/CloudBackup/issues). 

## Show your support

Give a ⭐️ if this project helped you!

## 📝 License

Copyright © 2023 [Voinov Andrey](https://github.com/gx56q).<br />
This project is [MIT license](https://github.com/gx56q/CloudBackup/blob/master/LICENSE) licensed.

***