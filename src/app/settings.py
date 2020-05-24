"""
Settings for cardpay project.
"""
import os

import environ


root = environ.Path(__file__) - 2  # path to root folder
env = environ.Env(DEBUG=(bool, False))
environ.Env.read_env(os.path.join(root, '.env'))

"""
SECURITY WARNING:
- keep the secret key used in production secret!
- don't run with debug turned on in production!
"""
SECRET_KEY = env('SECRET_KEY')
DEBUG = env('DEBUG', cast=bool, default=False)
ALLOWED_HOSTS = ['*']  # host validation is not necessary

# Application definition

INSTALLED_APPS = [
    'rest_framework',

    'payments',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.middleware.common.CommonMiddleware',
]

ROOT_URLCONF = 'app.urls'
WSGI_APPLICATION = 'app.wsgi.application'

# Internationalization

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_TZ = True

# Logging

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} | {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django.request': {
            'handlers': ['console'],
            'level': 'DEBUG',
        },
        'payments': {
            'handlers': ['console'],
            'level': 'INFO',
        },
    },
}

# 3d party packages

REST_FRAMEWORK = {
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
    ],
    'DEFAULT_PARSER_CLASSES': [
        'rest_framework.parsers.JSONParser',
    ],
}
