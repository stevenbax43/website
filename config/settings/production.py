from .base import *

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv('SECRET_KEY_prod')  

ALLOWED_HOSTS = ['stevenbaxontwerpt.nl'] #['*'] = iedereen toegang

# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases
# connect to created database postgresql on the Virtual machine on google cloud platform.
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('name_db'),
        'USER':  os.environ.get('user_db'), #oude stevenbax
        'PASSWORD': os.environ.get('password_db'), #oude 3173
        'HOST':'localhost',
        'PORT':'',
    }
}

# Static files (CSS, JavaScript, images)
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR , 'assets/')

# Media files
MEDIA_URL = '/media/'

