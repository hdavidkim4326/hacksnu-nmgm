"""
Django settings for a DB-less Vercel deployment.
This version is configured to work correctly in both local development
and Vercel production environments.
"""
from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'django-insecure-t!%r)zhdm56%j5_)4bt)78ei!cwil8v-bu+jj@rk0!8+6j)@^a'

# Vercel's 'VERCEL_ENV' variable is used to distinguish between environments.
# It will be 'production' on Vercel, and won't exist locally,
# so DEBUG will be True locally and False in production.
DEBUG = os.environ.get('VERCEL_ENV') != 'production'

ALLOWED_HOSTS = ['*']

# Application definition - MINIMAL set for a DB-less site
INSTALLED_APPS = [
    'django.contrib.staticfiles',
    'nmgm',
]

# MIDDLEWARE - MINIMAL set for a DB-less site
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    # 'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

# TEMPLATES - MINIMAL set without DB-dependent context processors
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

# Database - COMPLETELY DISABLED
DATABASES = {}

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = 'static/'
STATICFILES_DIRS = [
    BASE_DIR / 'nmgm' / 'static',
]
STATIC_ROOT = BASE_DIR / 'staticfiles'
# STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'


# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

