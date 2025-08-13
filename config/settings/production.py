# production.py
from .base import *
import os, sys

# ----- Secrets -----
SECRET_KEY = os.getenv('SECRET_KEY_prod')

# ----- Hosts / CSRF -----
ALLOWED_HOSTS = [
    'stevenbaxontwerpt.nl',
    'www.stevenbaxontwerpt.nl',
]

# Django 4.x+ requires full scheme for trusted origins
CSRF_TRUSTED_ORIGINS = [
    'https://stevenbaxontwerpt.nl',
    'https://www.stevenbaxontwerpt.nl',
]

# If nginx terminates TLS and forwards X-Forwarded-Proto (it does in your config),
# tell Django to trust that header:
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# ----- HTTPS only -----
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

# SameSite defaults are reasonable; keep Lax unless you know you need cross-site embeds
SESSION_COOKIE_SAMESITE = 'Lax'
CSRF_COOKIE_SAMESITE = 'Lax'

# Optional: make cookies HttpOnly (prevents JS access).
# Only enable CSRF_COOKIE_HTTPONLY if you are NOT reading the CSRF cookie via JS.
SESSION_COOKIE_HTTPONLY = True
# CSRF_COOKIE_HTTPONLY = True  # uncomment if you never read CSRF cookie in JS

# ----- HSTS (enable gradually) -----
# Start small to test (e.g., 300 seconds), then raise to 31536000 and set preload/includeSubDomains.
SECURE_HSTS_SECONDS = int(os.getenv('SECURE_HSTS_SECONDS', 0))  # set to 300 first, then 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# ----- Clickjacking / MIME sniffing / Referrer policy (Django adds some; keep explicit) -----
X_FRAME_OPTIONS = 'DENY'
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_REFERRER_POLICY = 'same-origin'  # or 'strict-origin-when-cross-origin'

# ----- Database -----
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('name_db'),
        'USER': os.getenv('user_db'),
        'PASSWORD': os.getenv('password_db'),
        'HOST': 'localhost',
        'PORT': '5432',
        # Optional: safer defaults
        'CONN_MAX_AGE': 60,          # keep connections pooled for a minute
        'ATOMIC_REQUESTS': True,     # wrap each view in a transaction
    },
}

# ----- Static / Media -----
# Nginx serves /static and /media; keep manifest storage for cache-busting
STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.ManifestStaticFilesStorage'

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media/')

# ----- Upload limits (pair with nginx client_max_body_size) -----
DATA_UPLOAD_MAX_MEMORY_SIZE = 100 * 1024 * 1024   # 100 MB
FILE_UPLOAD_MAX_MEMORY_SIZE = 100 * 1024 * 1024

# ----- Logging -----
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {'class': 'logging.StreamHandler', 'stream': sys.stdout},
    },
    'root': {'handlers': ['console'], 'level': 'INFO'},
    'loggers': {
        'django.server': {'handlers': ['console'], 'level': 'INFO', 'propagate': False},
        'django.request': {'handlers': ['console'], 'level': 'ERROR', 'propagate': False},
        # Log security-related events (for 403s, CSRF, etc.)
        'django.security': {'handlers': ['console'], 'level': 'WARNING', 'propagate': False},
    },
}

# ----- Optional: extra hardening / diagnostics -----
# USE_X_FORWARDED_HOST = True   # only if you need to trust X-Forwarded-Host (usually not required)
# SECURE_CROSS_ORIGIN_OPENER_POLICY = 'same-origin'  # Django 5+
# ADMINS = [('Your Name', 'you@example.com')]
# SERVER_EMAIL = 'django@stevenbaxontwerpt.nl'
