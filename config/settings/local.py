from .base import * 

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv('SECRET_KEY_dev')  

ALLOWED_HOSTS = ['127.0.0.1', '34.90.54.105']

# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

# connect to created database postgresql on the local machine.

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}
STATICFILES_FINDERS = [
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    # ...
]

# Static files (CSS, JavaScript, images)
STATIC_URL = '/static/'
STATICFILES_DIRS = [
    BASE_DIR / "assets",
]

# Media files
MEDIA_URL = '/media/'

# Use SMTP locally when configured; otherwise print reset emails in the console.
EMAIL_HOST = os.getenv('EMAIL_HOST', '')
EMAIL_PORT = int(os.getenv('EMAIL_PORT', '587'))
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD', '')
EMAIL_USE_TLS = os.getenv('EMAIL_USE_TLS', 'true').lower() == 'true'
DEFAULT_FROM_EMAIL = os.getenv('DEFAULT_FROM_EMAIL', EMAIL_HOST_USER)
EMAIL_DEBUG = True
EMAIL_BACKEND = (
    'accounts.email_backends.DebugSMTPEmailBackend'
    if EMAIL_HOST
    else 'django.core.mail.backends.console.EmailBackend'
)


LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,

    "handlers": {
        "file": {
            "level": "DEBUG",
            "class": "logging.FileHandler",
            "filename": os.path.join(BASE_DIR, "debug.log"),
            "encoding": "utf-8",   # ✅ CRUCIAAL
        },
        "console": {
            "class": "logging.StreamHandler",
            "level": "INFO",
        },
    },

    "loggers": {
        "django": {
            "handlers": ["file"],
            "level": "DEBUG",
            "propagate": True,
        },

        # ✅ Optioneel maar sterk aanbevolen:
        # voorkom extreem veel SQL-logging
        "django.db.backends": {
            "handlers": ["file"],
            "level": "WARNING",
            "propagate": False,
        },
        "accounts.email": {
            "handlers": ["console", "file"],
            "level": "INFO",
            "propagate": False,
        },
    },
}
