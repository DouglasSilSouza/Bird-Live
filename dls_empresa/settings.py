from django.contrib.messages import constants as messages
from pathlib import Path
import os
from app_payment.gerencianet.variaveis import GetSecret
variavel = GetSecret().get_secret()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY =  variavel["SECRET_KEY"]

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = variavel['DJANGO_DEBUG']

ALLOWED_HOSTS = ['*']
# ALLOWED_HOSTS = ['127.0.0.1', '0.0.0.0', 'localhost', 'bird-live.cbemsi222wm9.us-east-2.rds.amazonaws.com', 'bird-live-ewe.ngrok-free.app']

CSRF_TRUSTED_ORIGINS = [f'https://bird-live-ewe.ngrok-free.app']

# Application definition

INSTALLED_APPS = [
    'daphne',
    'channels',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'sslserver',
    'widget_tweaks',
    'app_authentication',
    'app_main',
    'app_payment',
    'ecommerce_cart',
    'ecommerce_main',
]

ASGI_APPLICATION = 'dls_empresa.asgi.application'

CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels.layers.InMemoryChannelLayer',
    },
}

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://127.0.0.1:6379/1",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        }
    }
}

ROOT_URLCONF = 'dls_empresa.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(BASE_DIR, 'templates'),
            ],
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

WSGI_APPLICATION = 'dls_empresa.wsgi.application'

MESSAGE_TAGS = {
    messages.DEBUG: 'alert-secondary',
    messages.INFO: 'alert-info',
    messages.SUCCESS: 'alert-success',
    messages.WARNING: 'alert-warning',
    messages.ERROR: 'alert-danger',
}


# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

DATABASES={
    "default": {
        "ENGINE": "django.db.backends.mysql",
        "NAME": variavel["NAME"],
        "USER": variavel["USER"],
        "PASSWORD": variavel["PASSWORD"],
        "HOST": variavel["HOST"],
        "PORT": variavel["PORT"],
        "OPTIONS": {
            'sql_mode': 'STRICT_ALL_TABLES',
            'charset': 'utf8mb4',
        },
    }
}

# DATABASES={
#     "default": {
#         "ENGINE": "django.db.backends.mysql",
#         "NAME": 'dls_empresa',
#         "USER": 'root',
#         "PASSWORD": '',
#         "HOST": 'localhost',
#         "PORT": '3306',
#         "OPTIONS": {
#             'sql_mode': 'STRICT_ALL_TABLES',
#             'charset': 'utf8mb4',
#         },
#     }
# }

# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = 'pt-br'

TIME_ZONE = 'America/Sao_Paulo'

USE_I18N = True

USE_L10N = True

USE_TZ = True

DEFAULT_CHARSET = 'utf-8'

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

STATIC_URL = '/templates/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static')

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

#Location of static files
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'templates'),
    os.path.join(BASE_DIR, 'staticfiles'),
]

# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'app_authentication.email_backend.EmailBackend',
]

AUTH_USER_MODEL = 'app_authentication.Cadastro'

EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"

EMAIL_HOST = 'smtp.gmail.com'
EMAIL_HOST_USER = variavel["ENVIOS_EMAIL"]
EMAIL_HOST_PASSWORD = variavel["SENHA_GOOGLE"]
EMAIL_USE_TLS = True
EMAIL_PORT = 587

THOUSAND_SEPARATOR='.',
USE_THOUSAND_SEPARATOR=True

APPEND_SLASH=False