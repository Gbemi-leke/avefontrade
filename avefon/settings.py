from pathlib import Path
from django.contrib.messages import constants as messages

BASE_DIR = Path(__file__).resolve().parent.parent
TEMPLATES_DIR = BASE_DIR / 'templates'
STATIC_DIR    = BASE_DIR / 'static'
MEDIA_ROOT    = BASE_DIR / 'media'
MEDIA_URL     = '/media/'
STATICFILES_DIRS = [STATIC_DIR]

SECRET_KEY = 'django-insecure-0wa6q5zowu0&h@wa=26s^*2nk3r(coj6cri(6=d+1jhr(ta1g#'
DEBUG      = True
ALLOWED_HOSTS = ['*']

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'frontend',
    'backend',
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

ROOT_URLCONF = 'avefon.urls'

TEMPLATES = [{
    'BACKEND': 'django.template.backends.django.DjangoTemplates',
    'DIRS': [TEMPLATES_DIR],
    'APP_DIRS': True,
    'OPTIONS': {'context_processors': [
        'django.template.context_processors.request',
        'django.contrib.auth.context_processors.auth',
        'django.contrib.messages.context_processors.messages',
    ]},
}]

WSGI_APPLICATION = 'avefon.wsgi.application'

DATABASES = {'default': {
    'ENGINE': 'django.db.backends.sqlite3',
    'NAME': BASE_DIR / 'db.sqlite3',
}}

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
     'OPTIONS': {'min_length': 6}},
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE     = 'Africa/Accra'
USE_I18N = True
USE_TZ   = True

STATIC_URL = 'static/'
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

LOGIN_URL          = '/login/'
LOGIN_REDIRECT_URL = '/dashboard/'
LOGOUT_REDIRECT_URL = '/'

MESSAGE_TAGS = {
    messages.DEBUG:   'alert-info',
    messages.INFO:    'alert-info',
    messages.SUCCESS: 'alert-success',
    messages.WARNING: 'alert-warning',
    messages.ERROR:   'alert-danger',
}


# ── Africa's Talking SMS ──────────────────────────────────────
AT_USERNAME = 'sandbox'   # Change to your real username when going live
AT_API_KEY  = 'atsk_f2b1fc7ed712c915a38122d7f90bd0ebe029eb7bbc1fca1702d580de7d3a64ab1cd231a1'
AT_SENDER   = 'AVEFON'    # Your sender ID (may need approval for live)