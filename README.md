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

### Configure MySQL datebase

```shell
(blog)$  mysql -uroot -p
```

- Create new database: basic_blog

```mysql
mysql> CREATE DATABASE basic_blog CHARSET utf8;
```

- Create new user for database: itheima

```mysql
mysql> CREATE USER itheima identified BY '123456';
```

- Authorize the 'itheima' to access the 'basic_blog'

```mysql
mysql> GRANT ALL ON basic_blog.* TO 'itheima'@'%';
```

- refresh

```mysql
mysql> FLUSH PRIVILEGES;
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

### Configure Redis Database

- Install django-redis extension package

```shell
(blog)$ pip install django-redis
```

- modify the `settings.py`

```python
# Redis
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://127.0.0.1:6379/0",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        }
    },
    "session": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://127.0.0.1:6379/1",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        }
    },
}
# change session from database to redis
SESSION_ENGINE = "django.contrib.sessions.backends.cache"
SESSION_CACHE_ALIAS = "session"
```

- start redis-serever

```
$ redis-server
```

- test the server

```shell
(blog)$ python manage.py runserver
```

### static page

- copy static to blog directory

- modify `settings.py`

```python
# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.2/howto/static-files/

STATIC_URL = '/static/'
# set static resource directory
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
]
```

## register page in 6 steps

### Create users page

- Create sub app users

```shell
(blog)$ python manage.py startapp users
```

- register sub app `settings.py`

```python
# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # sub app register
    'users.apps.UsersConfig',
]
```

### Create Templates

- create templates in the same directory with users and static
- modify the `settings.py`

```python
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],	# modify here
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]
```

- move `static/prism/register.html` to `templates/`

- modify `users/views.py`

```python
from django.views import View

# Register view
class RegisterView(View):
    def get(self, request):
        return render(request, 'register.html')
```

- create a file named `urls.py` in the directory `users`

```python
# for route view of users sub app 
from django.urls import path
from users.views import RegisterView

urlpatterns = {
    # first arg: route
    # second arg: view function name
    path('register/', RegisterView.as_view(), name='register'),
}
```

- modify `blog/blog/blog/urls.py`

```python
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include(('users.urls', 'users'), namespace='users'))
]
```

### Use Template Language

modify `templates/register.html`

```html
{% load staticfiles %} # add this
    <!-- 引入bootstrap的css文件 -->
    <link rel="stylesheet" href="{% static 'bootstrap/css/bootstrap.min.css' %}"> # modify
    <!-- 引入vuejs -->
    <script type="text/javascript" src="{% static 'js/vue-2.5.16.js' %}"></script>
    <script type="text/javascript" src="{% static 'js/axios-0.18.0.min.js' %}"></script>
```

### Authorization

#### Define user model

 `users->models.py`

```python
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    # phone number
    mobile = models.CharField(max_length=11, unique=True, blank=False)
    # avatar, ImageField need pip install Pillow first.
    avatar = models.ImageField(upload_to='avatar/%Y%m%d/', blank=True)
    # description
    user_desc = models.CharField(max_length=500, blank=True)

class Meta:
    db_table = 'tb_users'   # modify name of table
    verbose_name = 'User Management'
    verbose_name_plural = verbose_name  # admin backstage display

def __str__(self):
    return self.mobile
```

#### Specified user model class

`setting.py`, add

```python
# Replace the 'User' of system, and use our own defined 'User'
# 'sub app's name.model class'
AUTH_USER_MODEL = 'users.User' 
```

#### Generate migration file

```shell
(blog)$ python manage.py makemigrations
```

> Migrations for 'users':
>   users/migrations/0001_initial.py
>     - Create model User

If error occurs, maybe you should insatll pillow

```shell
(blog)$ pip install Pillow
```

#### Execute migration

```shell
(blog)$ python manage.py migrate
```

#### check MySQL table

- Open the MySQL

```shell
mysql -u root -p
```

- Show tables

```mysql
mysql> SHOW TABLES;
```

> +-----------------------------+
> | Tables_in_basic_blog        |
> +-----------------------------+
> | auth_group                  |
> | auth_group_permissions      |
> | auth_permission             |
> | django_admin_log            |
> | django_content_type         |
> | django_migrations           |
> | django_session              |
> | users_user                  |
> | users_user_groups           |
> | users_user_user_permissions |
> +-----------------------------+
> 10 rows in set (0.001 sec)

- show tb_users.

