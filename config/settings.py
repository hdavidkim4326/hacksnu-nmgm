"""
Django settings for a DB-less Vercel deployment.
This version is configured to work correctly in both local development
and Vercel production environments.
"""
from pathlib import Path
<<<<<<< HEAD
import environ

env = environ.Env()

environ.Env.read_env(env_file=".env")
=======
import os
>>>>>>> 3dd8b20559b1cf4fb28fc32a7b00c1f326172efe

BASE_DIR = Path(__file__).resolve().parent.parent

<<<<<<< HEAD
# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "django-insecure-t!%r)zhdm56%j5_)4bt)78ei!cwil8v-bu+jj@rk0!8+6j)@^a"
=======
SECRET_KEY = 'django-insecure-t!%r)zhdm56%j5_)4bt)78ei!cwil8v-bu+jj@rk0!8+6j)@^a'
>>>>>>> 3dd8b20559b1cf4fb28fc32a7b00c1f326172efe

# Vercel's 'VERCEL_ENV' variable is used to distinguish between environments.
# It will be 'production' on Vercel, and won't exist locally,
# so DEBUG will be True locally and False in production.
DEBUG = os.environ.get('VERCEL_ENV') != 'production'

ALLOWED_HOSTS = ['*']

# Application definition - MINIMAL set for a DB-less site
INSTALLED_APPS = [
<<<<<<< HEAD
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "nmgm",
=======
    'django.contrib.staticfiles',
    'nmgm',
>>>>>>> 3dd8b20559b1cf4fb28fc32a7b00c1f326172efe
]

# MIDDLEWARE - MINIMAL set for a DB-less site
MIDDLEWARE = [
<<<<<<< HEAD
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
=======
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
>>>>>>> 3dd8b20559b1cf4fb28fc32a7b00c1f326172efe
]

ROOT_URLCONF = "config.urls"

# TEMPLATES - MINIMAL set without DB-dependent context processors
TEMPLATES = [
    {
<<<<<<< HEAD
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
=======
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
>>>>>>> 3dd8b20559b1cf4fb28fc32a7b00c1f326172efe
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

<<<<<<< HEAD

# Database
# https://docs.djangoproject.com/en/5.2/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "HOST": env("DB_HOST"),
        "NAME": env("DB_NAME"),
        "USER": env("DB_USER"),
        "PASSWORD": env("DB_PASSWORD"),
        "PORT": env("DB_PORT"),
    }
}


# Password validation
# https://docs.djangoproject.com/en/5.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# Internationalization
# https://docs.djangoproject.com/en/5.2/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

=======
# Database - COMPLETELY DISABLED
DATABASES = {}

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
>>>>>>> 3dd8b20559b1cf4fb28fc32a7b00c1f326172efe
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATICFILES_DIRS = [
    BASE_DIR / 'nmgm' / 'static',
]
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

<<<<<<< HEAD
STATIC_URL = "static/"

# Default primary key field type
# https://docs.djangoproject.com/en/5.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
=======
WHITENOISE_USE_FINDERS = True

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

>>>>>>> 3dd8b20559b1cf4fb28fc32a7b00c1f326172efe
