import os
from pathlib import Path

from dotenv import load_dotenv

from core.https import https_settings

BASE_DIR = Path(__file__).resolve().parent.parent

load_dotenv(BASE_DIR.parent / '.env')

SITE_ID = 1


def env_bool(name, default=False):
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {'1', 'true', 'yes', 'on'}


SECRET_KEY = os.environ['SECRET_KEY']

DEBUG = env_bool('DEBUG', default=False)

_https = https_settings(DEBUG)
SECURE_SSL_REDIRECT = _https['SECURE_SSL_REDIRECT']
SESSION_COOKIE_SECURE = _https['SESSION_COOKIE_SECURE']
CSRF_COOKIE_SECURE = _https['CSRF_COOKIE_SECURE']
SECURE_HSTS_SECONDS = _https['SECURE_HSTS_SECONDS']
SECURE_HSTS_INCLUDE_SUBDOMAINS = _https['SECURE_HSTS_INCLUDE_SUBDOMAINS']
SECURE_CONTENT_TYPE_NOSNIFF = _https['SECURE_CONTENT_TYPE_NOSNIFF']
SECURE_PROXY_SSL_HEADER = _https['SECURE_PROXY_SSL_HEADER']

ALLOWED_HOSTS = [
    host.strip()
    for host in os.getenv('ALLOWED_HOSTS', '').split(',')
    if host.strip()
]

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.sites',
    'django.contrib.sitemaps',
    'django.contrib.staticfiles',
    'django.contrib.postgres',

    'taggit',

    'blog.apps.BlogConfig',
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

ROOT_URLCONF = 'core.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'core.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ['POSTGRES_DB'],
        'USER': os.environ['POSTGRES_USER'],
        'PASSWORD': os.environ['POSTGRES_PASSWORD'],
        'HOST': os.getenv('POSTGRES_HOST', '127.0.0.1'),
        'PORT': os.getenv('POSTGRES_PORT', '5432'),
    }
}

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

LANGUAGE_CODE = os.getenv('LANGUAGE_CODE', 'ru')

TIME_ZONE = os.getenv('TIME_ZONE', 'Europe/Moscow')

USE_I18N = env_bool('USE_I18N', default=True)

USE_TZ = env_bool('USE_TZ', default=True)

STATIC_URL = os.getenv('STATIC_URL', 'static/')
MEDIA_URL = os.getenv('MEDIA_URL', 'media/')
MEDIA_ROOT = BASE_DIR / 'media'

email_port = int(os.getenv('EMAIL_PORT', '587'))
email_use_ssl = env_bool('EMAIL_USE_SSL', default=email_port == 465)
email_use_tls = env_bool('EMAIL_USE_TLS', default=False) and not email_use_ssl

DEFAULT_FROM_EMAIL = os.getenv('DEFAULT_FROM_EMAIL', 'webmaster@localhost')

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'plain': {
            'format': '%(asctime)s %(levelname)s %(name)s %(message)s',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'plain',
        },
    },
    'loggers': {
        'blog': {
            'handlers': ['console'],
            'level': 'INFO',
        },
    },
}

MAILERS = {
    'default': {
        'BACKEND': 'django.core.mail.backends.smtp.EmailBackend',
        'OPTIONS': {
            'host': os.getenv('EMAIL_HOST', ''),
            'port': email_port,
            'username': os.getenv('EMAIL_HOST_USER', ''),
            'password': os.getenv('EMAIL_HOST_PASSWORD', ''),
            'use_tls': email_use_tls,
            'use_ssl': email_use_ssl,
        },
    },
}
