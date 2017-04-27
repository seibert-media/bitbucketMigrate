## Bitbucket Migrate
This little python script allows mirroring all projects including permissions and code to another bitbucket instance.
It creates copies of projects and it's repos and then does a local checkout of each repo/branch to push it back to the new remote.

### Requirements
- Python 3.5.3
- Git 2.2.x

### Usage
Define the Systems in migrate.cfg and set an admin user for both systems.

It is recommended to allow credential caching for git, as every action would require a new login
```
git config --global credential.helper "cache --timeout=3600"
```

To get started quickly, run it in a docker container
```
docker run -it --rm -v $PWD:/root/migrate python:3.5.3-alpine /bin/sh
~# cd /root/migrate
~# apk update
~# apk add git
~# pip3 install -r requirements.txt
~# ./migrate.py
``` 

Please note that all git repositories are getting cloned into ./temp/projectKey/repoSlug and that this takes some space.
Also not that large push actions to the target system may take a huge amount of RAM and CPU, so take care of that before you start.

### Todo
There might be the need to allow more flexible mirroring. At the moment only direct mirroring of projects is possible and there is no way of changing project keys etc.
In the future more features might be added, like also syncing project icons, settings and git lfs.
