"""
Django settings para BaixaFy Desktop Application
Configuração otimizada para execução local
"""

import os
import sys
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Detectar se está rodando como executável PyInstaller
if getattr(sys, 'frozen', False):
    # Rodando como executável
    APPLICATION_PATH = os.path.dirname(sys.executable)
    BASE_DIR = Path(APPLICATION_PATH)
else:
    # Rodando como script Python normal
    APPLICATION_PATH = os.path.dirname(os.path.abspath(__file__))

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'baixafy-desktop-secret-key-change-in-production-12345'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True  # Para desktop, mantemos True para melhor debugging

ALLOWED_HOSTS = ['127.0.0.1', 'localhost']

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'core',  # App principal do BaixaFy
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

ROOT_URLCONF = 'baixafy.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
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

WSGI_APPLICATION = 'baixafy.wsgi.application'

# Database - SQLite local para desktop
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'database' / 'baixafy_desktop.sqlite3',
    }
}

# Password validation
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
LANGUAGE_CODE = 'pt-br'
TIME_ZONE = 'America/Sao_Paulo'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]

# Media files (Downloads)
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'downloads'

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Configurações específicas do BaixaFy Desktop
BAIXAFY_SETTINGS = {
    'DOWNLOADS_PATH': BASE_DIR / 'downloads',
    'DATABASE_PATH': BASE_DIR / 'database',
    'SPOTDL_PATH': BASE_DIR / 'spotdl',
    'LICENSE_FILE': BASE_DIR / 'license.dat',
    'MAX_FREE_DOWNLOADS': 1,
    'TRIAL_DAYS': 30,
}

# Login/Logout URLs
LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/login/'

# Configurações de sessão para desktop
SESSION_COOKIE_AGE = 86400  # 24 horas
SESSION_COOKIE_NAME = 'baixafy_desktop_session'
SESSION_ENGINE = 'django.contrib.sessions.backends.db'

# Logging configuration para desktop
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': BASE_DIR / 'baixafy.log',
        },
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file', 'console'],
            'level': 'INFO',
            'propagate': True,
        },
        'baixafy': {
            'handlers': ['file', 'console'],
            'level': 'DEBUG',
            'propagate': True,
        },
    },
}

# Criar diretórios necessários se não existirem
os.makedirs(BAIXAFY_SETTINGS['DOWNLOADS_PATH'], exist_ok=True)
os.makedirs(BAIXAFY_SETTINGS['DATABASE_PATH'], exist_ok=True)
os.makedirs(BASE_DIR / 'logs', exist_ok=True)