import sys
from pathlib import Path
import environ

env = environ.Env()
DEBUG = True
SECRET_KEY = 'CHANGE_THIS_TO_SOMETHING_UNIQUE_AND_SECURE'

PROJECT_ROOT = Path(__file__).parent.absolute()
GUARDIAN_MODULE_PATH = PROJECT_ROOT.parent.absolute()
sys.path.insert(0, GUARDIAN_MODULE_PATH)

DATABASES = {'default': env.db(default="sqlite://./example.db")}

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.admin',
    'django.contrib.messages',
    'guardian',
    'posts',
    'articles',
    'core',
    'django.contrib.staticfiles',
)

MIDDLEWARE = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
)

STATIC_ROOT = GUARDIAN_MODULE_PATH / 'public' / 'static'
STATIC_URL = '/static/'
STATICFILES_DIRS = [PROJECT_ROOT / 'static']
GUARDIAN_RAISE_403 = True

ROOT_URLCONF = 'urls'

SITE_ID = 1

USE_I18N = True
USE_L10N = True

LOGIN_REDIRECT_URL = '/'

TEST_RUNNER = 'django.test.runner.DiscoverRunner'

AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
    'guardian.backends.ObjectPermissionBackend',
)

GUARDIAN_GET_INIT_ANONYMOUS_USER = 'core.models.get_custom_anon_user'

PASSWORD_HASHERS = (
    'django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher',
)

AUTH_USER_MODEL = 'core.CustomUser'
GUARDIAN_USER_OBJ_PERMS_MODEL = 'articles.BigUserObjectPermission'
GUARDIAN_GROUP_OBJ_PERMS_MODEL = 'articles.BigGroupObjectPermission'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': (
            PROJECT_ROOT / 'templates',
        ),
        'OPTIONS': {
            'debug': DEBUG,
            'loaders': (
                'django.template.loaders.filesystem.Loader',
                'django.template.loaders.app_directories.Loader',
            ),
            'context_processors': (
                'core.context_processors.version',
                'django.contrib.auth.context_processors.auth',
                'django.template.context_processors.debug',
                'django.template.context_processors.i18n',
                'django.template.context_processors.media',
                'django.template.context_processors.static',
                'django.template.context_processors.request',
                'django.template.context_processors.tz',
                'django.contrib.messages.context_processors.messages'
            ),
        },
    },
]
