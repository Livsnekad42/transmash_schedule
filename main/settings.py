"""
Django settings for main project.

Generated by 'django-admin startproject' using Django 4.0.1.

For more information on this file, see
https://docs.djangoproject.com/en/4.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.0/ref/settings/
"""
import os
from datetime import timedelta
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
import redis
from kombu import Queue, Exchange


BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-mnsk^a^d0k-_g@trb+@aw27@ay2qcjwq=(7tn*!a&n2+pdomf_'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

APP_HOST = "memory-candle.web-intellect.com"

ALLOWED_HOSTS = ["127.0.0.1", APP_HOST, "memory-flower.ru", "*"]


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'rest_framework',
    'rest_framework_swagger',
    'geoip2',

    'authentication',
    'profiles',
    'geo_city',
    'company',
    'notification',
    'administration',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'main.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': ['templates'],
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

WSGI_APPLICATION = 'main.wsgi.application'


# Database
# https://docs.djangoproject.com/en/4.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
}

CACHE_TTL = 60 * 1

# Password validation
# https://docs.djangoproject.com/en/4.0/ref/settings/#auth-password-validators

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

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

AUTH_USER_MODEL = 'authentication.User'


# Internationalization
# https://docs.djangoproject.com/en/3.1/topics/i18n/

LANGUAGE_CODE = 'ru'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

LOGIN_URL = '/'

GEOIP_PATH = os.path.join(BASE_DIR, "mmdb")

# DRF
APPEND_SLASH = True
REST_FRAMEWORK = {
    # Use Django's standard `django.contrib.auth` permissions,
    # or allow read-only access for unauthenticated users.
    'DEFAULT_AUTHENTICATION_CLASSES': (
        # 'rest_framework_jwt.authentication.JSONWebTokenAuthentication',
        'rest_framework.authentication.SessionAuthentication',
        'authentication.backends.JSONWebTokenAuthentication'
    ),

    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],

    'DEFAULT_MODEL_SERIALIZER_CLASS':
        'rest_framework.serializers.HyperlinkedModelSerializer',

    'PAGE_SIZE': 20,

    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.LimitOffsetPagination',

    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',
    ),

    'JWT_AUTH_HEADER_PREFIX': 'Bearer',

    'JWT_ALLOW_REFRESH': True,

    'EXCEPTION_HANDLER': 'core.exceptions.core_exception_handler',

    'NON_FIELD_ERRORS_KEY': 'detail',
}

JWT_AUTH = {
    'JWT_AUTH_HEADER_PREFIX': 'Bearer',
    'JWT_EXPIRATION_DELTA': timedelta(minutes=30),
}

SWAGGER_SETTINGS = {
    'SHOW_REQUEST_HEADERS': True,
    'SECURITY_DEFINITIONS': {
        'Bearer': {
            'type': 'apiKey',
            'name': 'Authorization',
            'in': 'header'
        }
    },
    'USE_SESSION_AUTH': False,
    'JSON_EDITOR': True,
    'SUPPORTED_SUBMIT_METHODS': [
        'get',
        'post',
        'put',
        'delete',
        'patch'
    ],
}

#CELERY
REDIS_HOST = 'localhost'
REDIS_PORT = '6379'
BROKER_URL = 'redis://' + REDIS_HOST + ':' + REDIS_PORT + '/0'
BROKER_TRANSPORT_OPTIONS = {'visibility_timeout': 13600}

CELERY_RESULT_BACKEND = 'redis://' + REDIS_HOST + ':' + REDIS_PORT + '/0'
CELERY_BROKER_URL = 'redis://' + REDIS_HOST + ':' + REDIS_PORT + '/0'
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_IGNORE_RESULT = True
CELERYD_PREFETCH_MULTIPLIER = 2
CELERYD_MAX_TASKS_PER_CHILD = 5
CELERY_DISABLE_RATE_LIMITS = True
CELERY_SEND_TASK_ERROR_EMAILS = True
CELERND_TASK_ERROR_EMAILS = True
CELERYD_FORCE_EXECV = True

CELERY_QUEUES = (
    Queue('default', Exchange('default'), routing_key='default'),
    Queue('notify_worker', Exchange('notify_worker'), routing_key='notify_worker'),
)

CELERY_DEFAULT_QUEUE = 'default'
CELERY_DEFAULT_EXCHANGE = 'default'
CELERY_DEFAULT_ROUTING_KEY = 'default'

CELERY_ROUTES = {
    'authentication.tasks.send_verification_email': {'queue': 'notify_worker'},
    'authentication.tasks.verification_sms_api': {'queue': 'notify_worker'},
    'notification.tasks.send_email': {'queue': 'notify_worker'},
    'notification.tasks.send_sms': {'queue': 'notify_worker'},
    'notification.tasks.send_notification_user_requests': {'queue': 'notify_worker'},
}

REDIS_CONNECT = redis.Redis(db=3)

STATIC_ROOT = os.path.join(BASE_DIR, 'statics')
STATICFILES_DIRS = (os.path.join(BASE_DIR, 'static'), )
STATIC_URL = '/static/'

MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
MEDIAFILES_DIRS = (os.path.join(BASE_DIR, 'media'), )
MEDIA_URL = '/media/'

# Время жизни кода из СМС
SMS_CODE_EXPIRATION_DELTA = timedelta(seconds=180)

# Через какое время можно повторно запросить код
SMS_REFRESH_CODE_EXPIRATION = timedelta(seconds=180)

# Время жизни кода из Email
EMAIL_CODE_EXPIRATION_DELTA = timedelta(minutes=10)

# Максимальное количество неудачных попыток войти в свой профиль
COUNT_FAILED_ATTEMPT = 10

# Время бана пользователя при исчерпании всех доступных попыток
BAN_TIME = timedelta(minutes=30)

# Макстимальщный размер загружаемых файлов Mb
MAX_UPLOAD_SIZE = 5

from main.local_settings import *
