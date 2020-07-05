"""
Django settings for csgame project.

Generated by 'django-admin startproject' using Django 1.11.1.

For more information on this file, see
https://docs.djangoproject.com/en/1.11/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.11/ref/settings/
"""

import os
import configparser
# Tricky lib to convert string to boolean directly in python.
from distutils.util import strtobool
import importlib.util

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
BASE_DIR =  os.path.dirname(PROJECT_ROOT)


# Get Environment Variables from .env
my_env = os.environ.copy()
parser = configparser.ConfigParser({k: v.replace('$', '$$') for k, v in os.environ.items()},
         interpolation=configparser.ExtendedInterpolation())
settingsFile = os.path.join(BASE_DIR, ".env")
if os.path.isfile(settingsFile):
    with open(settingsFile) as stream:
        parser.read_file(['[DEFAULT]\n', *stream])
        for k, v in parser["DEFAULT"].items():
            my_env.setdefault(k.upper(), v)

# Environment Variables Import
try:
    # Amazon s3 secret
    AWS_ACCESS_KEY_ID = my_env['AWS_ACCESS_KEY_ID']
    AWS_SECRET_ACCESS_KEY = my_env['AWS_SECRET_ACCESS_KEY']
    AWS_STORAGE_BUCKET_NAME = my_env['AWS_STORAGE_BUCKET_NAME']
    IS_PRODUCTION_SITE = strtobool(my_env['IS_PRODUCTION_SITE'])
    TEST_HTTP_HANDLING = strtobool(my_env.get('TEST_HTTP_HANDLING', 'False'))
    IS_GOOGLE_CLOUD = strtobool(my_env.get('IS_GOOGLE_CLOUD', 'False'))
    NUMROUNDS = {
        'phase01a': int(my_env.get('NUMROUNDS_STEP1', my_env.get('NUMROUNDS', '5'))), # step 1
        'phase01b': int(my_env.get('NUMROUNDS_STEP2', '5')), # step 2
        'phase03': 1 # step 3
    }

    # if not on google cloud
    if not IS_GOOGLE_CLOUD:
        print("I am not using googole cloud service!")
        # Set up database url
        DATABASE_URL = my_env.get('DATABASE_URL', None) or (
            'postgres://cam2cds:%s@cam2cds2020-dev.c2bvrno4ucam.us-east-2.rds.amazonaws.com:5432/cdsdev'
            % (my_env['POSTGRESQLPASS'],))
        # Database
        # https://docs.djangoproject.com/en/1.11/ref/settings/#databases
        import dj_database_url
        DATABASES = {'default': dj_database_url.config(default=DATABASE_URL, conn_max_age=600, ssl_require=True)}
    else:
        print("I am using google cloud service now!")
        DATABASES = {
        'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'HOST': os.environ['DB_HOST'],
        'PORT': os.environ['DB_PORT'],
        'NAME': os.environ['DB_NAME'],
        'USER': os.environ['DB_USER'],
        'PASSWORD': os.environ['DB_PASSWORD']
        }
    }

    # Environment variable for set up the dataset we are going to use. By default it will be airplanes folder for testing
    KEY = my_env.get('KEY', 'Caltech101/airplane/image_{:04d}.jpg')
    print(KEY);
    KEYRING = KEY.rsplit('/', 1)[0]+'/'
    OBJECT_NAME_PLURAL = my_env.get('OBJECT_NAME_PLURAL', KEY.split('/')[1]+'s')

except KeyError as e:
    exit('Lacking Environment Variables: ' + str(e)) # indicate to the OS that the program has failed



# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.11/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'jsl5xrm^in$mx)ftkdeybi0#(uqr)j=e=eer%eg2rxk#h#1l9r'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG=not(IS_PRODUCTION_SITE or TEST_HTTP_HANDLING)

ALLOWED_HOSTS = [
	'test-csgame.herokuapp.com',
    '127.0.0.1',
    'localhost',
    'cam2-crowdsourcing.herokuapp.com',
    'cam2-cds-test-243502.appspot.com',
]


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'users.apps.UsersConfig',
    'storages',
]

 # Optional applications that are not required for the working of the game
INSTALLED_APPS.extend(filter(importlib.util.find_spec, (
    'corsheaders',
    'rest_framework',
    'import_export',
    'jsoneditor',
)))

MIDDLEWARE = [
    # Simplified static file serving.
    # https://warehouse.python.org/project/whitenoise/
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'csgame.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
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

WSGI_APPLICATION = 'csgame.wsgi.application'



# Password validation
# https://docs.djangoproject.com/en/1.11/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/1.11/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'America/Indiana/Indianapolis'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.11/howto/static-files/
if not IS_GOOGLE_CLOUD:
    STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
    STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
else:
    STATIC_ROOT = os.path.join(os.path.dirname(BASE_DIR), 'cam2-cds-static')

STATIC_URL = my_env.get('STATIC_URL', '/static/')

STATICFILES_DIRS = (
    os.path.join(BASE_DIR, 'static'),
)


AUTH_USER_MODEL = 'users.CustomUser'

LOGIN_REDIRECT_URL = 'home'

LOGOUT_REDIRECT_URL = 'home'

# Cloud Service by amazon s-3
AWS_S3_CUSTOM_DOMAIN = '%s.s3.amazonaws.com' % AWS_STORAGE_BUCKET_NAME
AWS_S3_OBJECT_PARAMETERS = {
    'CacheControl': 'max-age=86400',
}
AWS_DEFAULT_ACL = None

# File upload ?
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
DATA_UPLOAD_MAX_MEMORY_SIZE = 1073741824

#Default file storage
DEFAULT_FILE_STORAGE = 'csgame.storage_backends.MediaStorage'

# Only enable the mturk link when we done with experimenting mturk sandbox
MTURK_URL = my_env.get('MTURK_URL', 'https://mturk-requester.us-east-1.amazonaws.com')
CSRF_TRUSTED_ORIGINS = ['mechanicalturk.amazonaws.com', 'mturk-requester-sandbox.us-east-1.amazonaws.com', 'workersandbox.mturk.com']
CSRF_COOKIE_SAMESITE = None

# for mturk iframe
X_FRAME_OPTIONS = 'ALLOWALL'
XS_SHARING_ALLOWED_METHODS = ['POST','GET','OPTIONS', 'PUT', 'DELETE']

if DEBUG:
    ALLOWED_HOSTS += ['fairvision.app.local']
