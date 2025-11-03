# project_settings/settings.py

# ==============================================================================
# IMPORTAÇÕES ESSENCIAIS
# ==============================================================================
import os 
from pathlib import Path
# from dotenv import load_dotenv  # Mantemos comentado para desenvolvimento local sem .env
# import dj_database_url  # Mantemos comentado
from whitenoise.storage import CompressedManifestStaticFilesStorage

# # Carrega variáveis do .env (Mantemos comentado)
# load_dotenv() 

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# ==============================================================================
# CONFIGURAÇÕES DE AMBIENTE
# ==============================================================================
# O código de URL foi removido daqui!
SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-chave-de-desenvolvimento-insegura')
DEBUG = True # Forçamos True para facilitar o desenvolvimento local
ALLOWED_HOSTS = os.environ.get(
    'ALLOWED_HOSTS', 
    '127.0.0.1,localhost,docebella-livrocaixa-iorl.onrender.com' # <--- Adicionado aqui
).split(',')

# ==============================================================================
# DEFINIÇÃO DA APLICAÇÃO
# ==============================================================================
INSTALLED_APPS = [
    # Apps Padrão do Django
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'import_export',
    'widget_tweaks',
    
    # Seus Apps
    'core',
    'clientes',
    'financeiro',
    'vendas',
    'precificacao',  
]


MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    # CORREÇÃO: Nome correto do middleware para servir estáticos (Whitenoise)
    'whitenoise.middleware.WhiteNoiseMiddleware', 
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'project_settings.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        # Configuração para buscar na pasta 'templates' na raiz
        'DIRS': [os.path.join(BASE_DIR, 'templates')],  
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

WSGI_APPLICATION = 'project_settings.wsgi.application'

# ==============================================================================
# DATABASE (CORRIGIDO PARA SQLite LOCAL)
# ==============================================================================
import dj_database_url

DATABASES = {
    'default': dj_database_url.config(
        default='postgresql://banco_fluxo_user:irqAZZKbezY12UrhR3Fga22R7T4vQbXp@dpg-d3t8ol24d50c73d5kh6g-a.oregon-postgres.render.com/banco_fluxo',
        conn_max_age=600,
        ssl_require=True
    )
}

# ==============================================================================
# VALIDAÇÃO DE SENHA, I18N, TZ (Sem alterações)
# ==============================================================================
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
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# ==============================================================================
# ARQUIVOS ESTÁTICOS
# ==============================================================================
STATIC_URL = 'static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles') 
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'), 
]

# Configuração para que o Whitenoise otimize (Será ignorado pois DEBUG=True)
if not DEBUG:
    STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Redireciona o usuário para o Dashboard após o login
LOGIN_REDIRECT_URL = '/' 

# Redireciona para o Dashboard após o logout
LOGOUT_REDIRECT_URL = '/'
LOGIN_URL = '/accounts/login/'
