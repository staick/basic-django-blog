# basic-django-blog
A simple Django blog designed by ITheima.

## Preparation

### Creating a Virtual Environment

```shell
python -m venv blog
```

> The virtual environment was not created successfully because ensurepip is not
> available.  On Debian/Ubuntu systems, you need to install the python3-venv
> package using the following command.
>
>     apt install python3.10-venv
>
> You may need to use sudo with that command.  After installing the python3-venv
> package, recreate your virtual environment.
>
> Failing command: ['/home/staick/Workspace/Github/basic-django-blog/blog/bin/python', '-Im', 'ensurepip', '--upgrade', '--default-pip']

```shell
sudo apt install python3.10-venv
```

```shell
source blog/bin/activate
```

### Install Django

```shell
pip install django==2.2
```

```shell
cd blog
django-admin startproject blog
```

Test server

```shell
cd blog
python manage
```

