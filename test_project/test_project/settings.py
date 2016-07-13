"""
Django settings for test_project project.

For more information on this file, see
https://docs.djangoproject.com/en/1.7/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.7/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
BASE_DIR = os.path.dirname(os.path.dirname(__file__))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.7/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'g%2!$p#nhp93+0=o$y8s14p$9#m*0%!4j#7b#9bp7m#8$4gxa1'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

TEMPLATE_DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'djradicale',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'test_project.urls'

WSGI_APPLICATION = 'test_project.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.7/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

# Internationalization
# https://docs.djangoproject.com/en/1.7/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.7/howto/static-files/

STATIC_URL = '/static/'

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'djradicale': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': True,
        },
    }
}

DJRADICALE_CONFIG = {
    'server': {
        'base_prefix': '/pim/',
        'realm': 'Radicale - Password Required',
    },
    'encoding': {
        'request': 'utf-8',
        'stock': 'utf-8',
    },
    'auth': {
        'type': 'custom',
        'custom_handler': 'djradicale.auth.django',
    },
    'rights': {
        'type': 'custom',
        'custom_handler': 'djradicale.rights.django',
    },
    'storage': {
        'type': 'custom',
        'custom_handler': 'djradicale.storage.django',
    },
    'well-known': {
        'carddav': '/pim/%(user)s/addressbook.vcf',
        'caldav': '/pim/%(user)s/calendar.ics',
    },
}

DJRADICALE_RIGHTS = {
    'rw': {
        'user': '.+',
        'collection': '^%(login)s/[a-z0-9\.\-_]+\.(vcf|ics)$',
        'permission': 'rw',
    },
    'rw-root': {
        'user': '.+',
        'collection': '^%(login)s$',
        'permission': 'rw',
    },
}
