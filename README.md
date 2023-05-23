<h1 align="center">Welcome to CloudBackup 👋</h1>
<p>
  <a href="https://github.com/gx56q/CloudBackup/blob/master/LICENSE" target="_blank">
    <img alt="License: MIT license" src="https://img.shields.io/badge/License-MIT license-yellow.svg" />
  </a>
</p>

> Utility for backing up files to remote storage

## Usage

```sh
python3 main.py --help
'''returns: 
  -c, --client_type [ftp|yadisk|cloud_mail]
                                  Client to use.  [required]
  -h, --host HOST                 FTP host.
  -u, --user USERNAME             Username.
  -p, --pass PASSWORD             Password.
  -t, --token TOKEN               OAuth token.
  -d, --download ('REMOTE_PATH', 'LOCAL_PATH')
                                  Download a file from the remote path to the
                                  local path.
  -up, --upload ('LOCAL_PATH', 'REMOTE_PATH')
                                  Upload a file from the local path to the
                                  remote path.
  -l, --list REMOTE_PATH          List files at the remote path.
  --help                          Show this message and exit.
  '''


```

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
