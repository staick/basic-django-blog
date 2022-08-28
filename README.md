# basic-django-blog
A simple Django blog designed by ITheima.

## Preparation

### Creating a Virtual Environment

```shell
$ python -m venv blog
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
$ sudo apt install python3.10-venv
```

```shell
$ source blog/bin/activate
```

### Install Django

```shell
# (blog)$ pip install django==2.2 trouble
(blog)$ pip install django==2.2	
```

```shell
(blog)$ cd blog
(blog)$ django-admin startproject blog
```

Test server

```shell
(blog)$ cd blog
(blog)$ python manage.py runserver
```

### Create MySQL datebase

```shell
(blog)$  mysql -uroot -p
```

- Create new database: basic_blog

```mysql
mysql> create database basic_blog charset utf8;
```

- Create new user for database: itheima

```mysql
mysql> create user itheima identified by '123456';
```

- Authorize the 'itheima' to access the 'basic_blog'

```mysql
mysql> grant all on basic_blog.* to 'itheima'@'%';
```

- refresh

```mysql
mysql> flush privileges;
```

- modify the blog > blog > blog > settings.py

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',   # database engine
        'HOST': '127.0.0.1',    # database host
        'PORT': 3306,   # database port
        'USER': 'itheima',  #database user
        'PASSWORD': '123456',   # database password
        'NAME': 'basic_blog', # database name
    },
}
```

- install PyMySQL model

```shell
(blog)$  pip install PyMySQL
```



- modify the blog > blog > blog > \__init__.py

```python
import pymysql
pymysql.install_as_MySQLdb()
```

- test the server

```shell
(blog)$ python manage.py runserver
```

 There may be some trouble if the django version==2.2

> File "basic-django-blog/blog/lib/python3.10/site-packages/django/db/backends/mysql/operations.py", line 146, in last_executed_query
>     query = query.decode(errors='replace')
> AttributeError: 'str' object has no attribute 'decode'. Did you mean: 'encode'?

solution

edit `basic-django-blog/blog/lib/python3.10/site-packages/django/db/backends/mysql/operations.py`

replace the 

```python
query = query.decode(errors='replace')
```

with

```python
query = errors='replace'
```

