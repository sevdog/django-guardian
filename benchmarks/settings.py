import environ

env = environ.Env()
SECRET_KEY = 'NO_NEED_SECRET'

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.sessions',
    'django.contrib.contenttypes',
    'django.contrib.admin',
    'django.contrib.sites',
    'guardian',
    'benchmarks',
)

DJALOG_LEVEL = 40

DATABASES = {'default': env.db(default="sqlite:///")}
