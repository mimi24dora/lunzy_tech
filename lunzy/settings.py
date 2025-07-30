from pathlib import Path
from django.contrib.messages import constants as messages

# --- BASE CONFIG ---
BASE_DIR = Path(__file__).resolve().parent.parent
SECRET_KEY = 'django-insecure-^1-fe-!5i*cso9so=9xgwm6*0fs3(juf1135ydwg+&co!2u-$f'
DEBUG = True
ALLOWED_HOSTS = ['127.0.0.1', 'localhost']

# --- MODELE UTILISATEUR PERSONNALISÉ ---
AUTH_USER_MODEL = 'gestion_employes.CustomUser'

# --- REDIRECTION AUTH ---
LOGIN_URL = 'gestion_employes:login'
LOGOUT_REDIRECT_URL = 'gestion_employes:login'
LOGIN_REDIRECT_URL = 'gestion_employes:dashboard'

# --- APPLIS DJANGO + PERSO ---
INSTALLED_APPS = [
    'django_otp',
    'django_otp.plugins.otp_totp',
    'two_factor',
    'django_otp.plugins.otp_static',
    'phonenumber_field',
    'django.contrib.staticfiles',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'gestion_employes',
    'crispy_forms',
    'crispy_bootstrap5',
]

# --- MIDDLEWARE ---
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'gestion_employes.middleware_ids.IDSMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'gestion_employes.middleware.AdminApprovalMiddleware',
    'django_otp.middleware.OTPMiddleware',
]

ROOT_URLCONF = 'lunzy.urls'

# --- TEMPLATES ---
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
                'gestion_employes.context_processors.user_permissions',
            ],
        },
    },
]

# --- WSGI ---
WSGI_APPLICATION = 'lunzy.wsgi.application'

# --- BASE DE DONNÉES ---
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# --- VALIDATION MOT DE PASSE ---
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

# --- INTERNATIONALISATION ---
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# --- STATIC FILES ---
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

# --- MEDIA FILES ---
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# --- COOKIES & SESSIONS ---
SESSION_COOKIE_AGE = 1800
SESSION_SAVE_EVERY_REQUEST = True
SESSION_EXPIRE_AT_BROWSER_CLOSE = True

# --- EMAIL ---
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# --- CRISPY FORMS ---
CRISPY_TEMPLATE_PACK = 'bootstrap5'
CRISPY_ALLOWED_TEMPLATE_PACKS = ['bootstrap5']

# --- MESSAGES ---
MESSAGE_TAGS = {
    messages.DEBUG: 'alert-info',
    messages.INFO: 'alert-info',
    messages.SUCCESS: 'alert-success',
    messages.WARNING: 'alert-warning',
    messages.ERROR: 'alert-danger',
}

# --- AUTO FIELD ---
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# --- LOGGING IDS ---
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'WARNING',
            'class': 'logging.FileHandler',
            'filename': BASE_DIR / 'ids_alerts.log',
        },
    },
    'loggers': {
        'gestion_employes.ids': {
            'handlers': ['file'],
            'level': 'WARNING',
            'propagate': True,
        },
    },
}
