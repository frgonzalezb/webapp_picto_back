import os

from datetime import timedelta
from dotenv import load_dotenv
from pathlib import Path


# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Get environment variables
load_dotenv(os.path.join(BASE_DIR, '.env'))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ["SECRET_KEY"]

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = eval(os.environ["DEBUG"])

ALLOWED_HOSTS = os.environ["ALLOWED_HOSTS"].split(' ')


# Application definition

BASE_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

THIRD_PARTY_APPS = [
    'rest_framework',
    'rest_framework.authtoken',
    'rest_framework_simplejwt',
    'corsheaders',
    'django_rest_passwordreset',
    'drf_yasg',
    'drf_recaptcha',
    'simple_history',
]

LOCAL_APPS = [
    'apps.api',
]

INSTALLED_APPS = BASE_APPS + THIRD_PARTY_APPS + LOCAL_APPS

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'simple_history.middleware.HistoryRequestMiddleware',
]

ROOT_URLCONF = 'conf.urls'

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

WSGI_APPLICATION = 'conf.wsgi.application'


# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': os.environ['DB_ENGINE'],
        'NAME': os.environ['DB_NAME'],
        'USER': os.environ['DB_USER'],
        'PASSWORD': os.environ['DB_PASSWORD'],
        'HOST': os.environ['DB_HOST'],
        'PORT': int(os.environ['DB_PORT']),
    }
}


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

LANGUAGE_CODE = 'es-cl'

TIME_ZONE = 'America/Santiago'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

STATIC_URL = 'static/'


# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# CORS settings
# https://pypi.org/project/django-cors-headers/

CORS_ALLOWED_ORIGINS = [os.environ["CORS_ALLOWED_ORIGINS"]]

CSRF_TRUSTED_ORIGINS = [os.environ["CSRF_TRUSTED_ORIGINS"]]

CORS_ALLOW_CREDENTIALS = eval(os.environ["CORS_ALLOW_CREDENTIALS"])



# Custom auth user model
AUTH_USER_MODEL = 'api.User'


# Custom Django REST Framework default settings
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_CACHE_CONTROL_MAX_AGE': int(os.environ["DEFAULT_CACHE_CONTROL_MAX_AGE"]),
    'DEFAULT_CACHE_CONTROL_PUBLIC': eval(os.environ["DEFAULT_CACHE_CONTROL_PUBLIC"]),
}


# SimpleJWT settings
# https://django-rest-framework-simplejwt.readthedocs.io/en/latest/settings.html

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=15),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=1),
    "ROTATE_REFRESH_TOKENS": eval(os.environ["ROTATE_REFRESH_TOKENS"]),
    "BLACKLIST_AFTER_ROTATION": eval(os.environ["BLACKLIST_AFTER_ROTATION"]),
    "UPDATE_LAST_LOGIN": eval(os.environ["UPDATE_LAST_LOGIN"]),

    "ALGORITHM": os.environ["ALGORITHM"],
    "SIGNING_KEY": os.environ["SECRET_KEY"],
    "VERIFYING_KEY": "",
    "AUDIENCE": eval(os.environ["AUDIENCE"]),
    "ISSUER": eval(os.environ["ISSUER"]),
    "JSON_ENCODER": eval(os.environ["JSON_ENCODER"]),
    "JWK_URL": eval(os.environ["JWK_URL"]),
    "LEEWAY": int(os.environ["LEEWAY"]),

    "AUTH_HEADER_TYPES": ("Bearer",),
    "AUTH_HEADER_NAME": "HTTP_AUTHORIZATION",
    "USER_ID_FIELD": "id",
    "USER_ID_CLAIM": "user_id",
    "USER_AUTHENTICATION_RULE": "rest_framework_simplejwt.authentication.default_user_authentication_rule",

    "AUTH_TOKEN_CLASSES": ("apps.api.tokens.CustomAccessToken",),
    "TOKEN_TYPE_CLAIM": "token_type",
    "TOKEN_USER_CLASS": "rest_framework_simplejwt.models.TokenUser",

    "JTI_CLAIM": "jti",

    "SLIDING_TOKEN_REFRESH_EXP_CLAIM": "refresh_exp",
    "SLIDING_TOKEN_LIFETIME": timedelta(minutes=5),
    "SLIDING_TOKEN_REFRESH_LIFETIME": timedelta(days=1),

    "TOKEN_OBTAIN_SERIALIZER": "rest_framework_simplejwt.serializers.TokenObtainPairSerializer",
    "TOKEN_REFRESH_SERIALIZER": "rest_framework_simplejwt.serializers.TokenRefreshSerializer",
    "TOKEN_VERIFY_SERIALIZER": "rest_framework_simplejwt.serializers.TokenVerifySerializer",
    "TOKEN_BLACKLIST_SERIALIZER": "rest_framework_simplejwt.serializers.TokenBlacklistSerializer",
    "SLIDING_TOKEN_OBTAIN_SERIALIZER": "rest_framework_simplejwt.serializers.TokenObtainSlidingSerializer",
    "SLIDING_TOKEN_REFRESH_SERIALIZER": "rest_framework_simplejwt.serializers.TokenRefreshSlidingSerializer",
}

SIMPLE_JWT.update({
    'AUTH_COOKIE': os.environ["COOKIE_NAME"],
})


# Email backend configuration
EMAIL_BACKEND = os.environ["EMAIL_BACKEND"]

EMAIL_PORT = int(os.environ["EMAIL_PORT"])

EMAIL_USE_TLS = eval(os.environ["EMAIL_USE_TLS"])

EMAIL_HOST = os.environ["EMAIL_HOST"]

EMAIL_HOST_USER = os.environ["EMAIL_HOST_USER"]

EMAIL_HOST_PASSWORD = os.environ["EMAIL_HOST_PASSWORD"]


# Django Rest Password Reset settings
# https://pypi.org/project/django-rest-passwordreset/

# Token life time in hours
DJANGO_REST_MULTITOKENAUTH_RESET_TOKEN_EXPIRY_TIME = 1


# Manejo de archivos media
MEDIA_URL = 'media/'

MEDIA_ROOT = os.environ['MEDIA_ROOT']


# reCAPTCHA settings
DRF_RECAPTCHA_SECRET_KEY = os.environ["DRF_RECAPTCHA_SECRET_KEY"]


# More Django settings
SECURE_SSL_REDIRECT = eval(os.environ['SECURE_SSL_REDIRECT'])

SECURE_HSTS_SECONDS = int(os.environ['SECURE_HSTS_SECONDS'])

SECURE_HSTS_PRELOAD = eval(os.environ['SECURE_HSTS_PRELOAD'])

SECURE_HSTS_INCLUDE_SUBDOMAINS = eval(os.environ['SECURE_HSTS_INCLUDE_SUBDOMAINS'])

SECURE_PROXY_SSL_HEADER = os.environ['SECURE_PROXY_SSL_HEADER'].split(',')

