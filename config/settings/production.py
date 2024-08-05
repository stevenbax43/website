from .base import *

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv('SECRET_KEY_prod')  

ALLOWED_HOSTS = ['35.204.155.206','stevenbaxontwerpt.nl'] #['*'] = iedereen toegang

# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases
# connect to created database postgresql on the Virtual machine on google cloud platform.
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('name_db'),
        'USER':  os.getenv('user_db'), #oude stevenbax
        'PASSWORD': os.getenv('password_db'), #oude 3173
        'HOST':'localhost',
        'PORT':'5432',
    }
}

AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
]
#f you are using HTTPS, set SECURE_SSL_REDIRECT to True in your settings.py to redirect all HTTP requests to HTTPS:
SECURE_SSL_REDIRECT = True

# Static files (CSS, JavaScript, images)
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR , 'assets/')

# Media files
MEDIA_URL = '/media/'

