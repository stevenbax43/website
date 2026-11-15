from .base import *
import sys
# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv('SECRET_KEY_prod')  

ALLOWED_HOSTS = ['35.204.155.206','stevenbaxontwerpt.nl', 'localhost', 'www.stevenbaxontwerpt.nl', '35.204.201.20'] #['*'] = iedereen toegang

# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases
# connect to created database postgresql on the Virtual machine on google cloud platform.
DATABASES = {
    'default': {
        "ENGINE": "django.db.backends.postgresql",
        'NAME': os.getenv('name_db'),
        'USER':  os.getenv('user_db'), 
        'PASSWORD': os.getenv('password_db'), 
        'HOST':'localhost',
        'PORT':'5432',
    },
}

# AUTHENTICATION_BACKENDS = [
#     'django.contrib.auth.backends.ModelBackend',
# ]
# #f you are using HTTPS, set SECURE_SSL_REDIRECT to True in your settings.py to redirect all HTTP requests to HTTPS:
# SECURE_SSL_REDIRECT = True

# Static files (CSS, JavaScript, images)
STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.ManifestStaticFilesStorage'

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media/')

# Configure these environment variables with the production SMTP provider.
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = os.getenv('EMAIL_HOST', '')
EMAIL_PORT = int(os.getenv('EMAIL_PORT', '587'))
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD', '')
EMAIL_USE_TLS = os.getenv('EMAIL_USE_TLS', 'true').lower() == 'true'
DEFAULT_FROM_EMAIL = os.getenv('DEFAULT_FROM_EMAIL', EMAIL_HOST_USER)

LOGGING = {
  "version": 1,
  "disable_existing_loggers": False,
  "handlers": {"console": {"class": "logging.StreamHandler", "stream": sys.stdout}},
  "root": {"handlers": ["console"], "level": "INFO"},
  "loggers": {
    "django.request": {"handlers": ["console"], "level": "ERROR", "propagate": False},
  },
}
DATA_UPLOAD_MAX_MEMORY_SIZE = 100 * 1024 * 1024
FILE_UPLOAD_MAX_MEMORY_SIZE = 100 * 1024 * 1024