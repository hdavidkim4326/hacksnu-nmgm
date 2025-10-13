"""
Django settings for a DB-less Vercel deployment.
"""
from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
SECRET_KEY = 'django-insecure-t!%r)zhdm56%j5_)4bt)78ei!cwil8v-bu+jj@rk0!8+6j)@^a'

# Vercel's environment will set this to False in production.
DEBUG = os.environ.get('DEBUG', 'False') == 'True'

# All hosts are allowed for this simple mockup site.
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
                # 'django.contrib.auth.context_processors.auth',      <- REMOVED
                # 'django.contrib.messages.context_processors.messages', <- REMOVED
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

# Database - COMPLETELY DISABLED
DATABASES = {}

# Password validation - REMOVED

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

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

