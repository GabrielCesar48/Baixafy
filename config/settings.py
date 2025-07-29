from pathlib import Path
from decouple import config
import os
import shutil
from pathlib import Path


# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = config('SECRET_KEY')
DEBUG = config('DEBUG', default=False, cast=bool)
ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='127.0.0.1').split(',')


# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # My apps
    'apps.core',
    'apps.baixador',
    'apps.users',
    
    # Third-party apps
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

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
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

WSGI_APPLICATION = 'config.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': config('DB_ENGINE', default='django.db.backends.sqlite3'),
        'NAME': BASE_DIR / config('DB_NAME', default='db.sqlite3'),
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


LANGUAGE_CODE = 'pt-br'
TIME_ZONE = 'America/Sao_Paulo'
USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Media files
MEDIA_URL = config('MEDIA_URL', default='/downloads/')
MEDIA_ROOT = BASE_DIR / config('MEDIA_ROOT', default='downloads')

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Custom User Model
AUTH_USER_MODEL = 'users.CustomUser'

# Login/Logout URLs
LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/painel/'
LOGOUT_REDIRECT_URL = '/'

# Messages Framework
from django.contrib.messages import constants as messages
MESSAGE_TAGS = {
    messages.DEBUG: 'debug',
    messages.INFO: 'info',
    messages.SUCCESS: 'success',
    messages.WARNING: 'warning',
    messages.ERROR: 'danger',
}



# 🔧 CONFIGURAÇÃO DO FFMPEG
def encontrar_ffmpeg():
    """Encontra FFmpeg automaticamente."""
    try:
        # 1. Verificar PATH primeiro
        ffmpeg_path = shutil.which('ffmpeg')
        if ffmpeg_path:
            return ffmpeg_path
        
        # 2. Locais comuns no Windows
        caminhos_comuns = [
            r'C:\ffmpeg\bin\ffmpeg.exe',
            r'C:\Program Files\ffmpeg\bin\ffmpeg.exe',
            r'C:\Program Files (x86)\ffmpeg\bin\ffmpeg.exe',
            Path.home() / 'ffmpeg' / 'bin' / 'ffmpeg.exe',
        ]
        
        for caminho in caminhos_comuns:
            if Path(caminho).exists():
                return str(caminho)
        
        return None
    except Exception as e:
        print(f"⚠️ Erro ao encontrar FFmpeg: {e}")
        return None

def criar_diretorios_seguro():
    """Cria diretórios necessários de forma segura."""
    try:
        # Criar diretório media
        media_dir = BASE_DIR / 'media'
        media_dir.mkdir(parents=True, exist_ok=True)
        
        # Criar diretório downloads
        downloads_dir = media_dir / 'downloads'
        downloads_dir.mkdir(parents=True, exist_ok=True)
        
        return downloads_dir
    except Exception as e:
        print(f"⚠️ Erro ao criar diretórios: {e}")
        # Retornar caminho mesmo que não consiga criar (será criado depois)
        return BASE_DIR / 'media' / 'downloads'

# Configurar caminho do FFmpeg de forma segura
try:
    FFMPEG_PATH = encontrar_ffmpeg()
    
    # Debug - mostrar no console apenas se encontrou
    if FFMPEG_PATH:
        print(f"✅ FFmpeg configurado: {FFMPEG_PATH}")
    else:
        print("❌ FFmpeg não encontrado - funcionalidade de download indisponível")
except Exception as e:
    print(f"⚠️ Erro na configuração do FFmpeg: {e}")
    FFMPEG_PATH = None

# 🎵 CONFIGURAÇÕES DO SPOTDL
SPOTIFY_CLIENT_ID = os.getenv('SPOTIFY_CLIENT_ID', '')
SPOTIFY_CLIENT_SECRET = os.getenv('SPOTIFY_CLIENT_SECRET', '')

# 📁 DIRETÓRIO DE DOWNLOADS - Criação segura
DOWNLOADS_ROOT = criar_diretorios_seguro()

# 🕒 CONFIGURAÇÕES DE TEMPO
DOWNLOAD_TIMEOUT = 300  # 5 minutos
CLEANUP_OLD_FILES = True  # Limpar arquivos antigos
CLEANUP_AFTER_HOURS = 24  # Limpar após 24 horas