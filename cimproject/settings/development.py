from .base import *

DEBUG = True

# Development database (you can change this later)
DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': 'cim_db',
        'USER': 'arthur',
        'PASSWORD': 'loadandload',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}

# Static files for development
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [
    BASE_DIR.parent / 'static',
]

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR.parent / 'media'

INSTALLED_APPS += [
    'django.contrib.gis',  # ← essential for GeoDjango
    # Local apps
    'apps.geo',
    'apps.services',
    'apps.users',
    'apps.locations',
    'apps.needs',
    'apps.businesses',
    'apps.main',
    'apps.heatmaps',
    'apps.subscriptions',
    'corsheaders',
]

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR.parent / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'apps.main.context_processors.yandex_maps',
            ],
        },
    },
]

#print("BASE_DIR =", BASE_DIR)
#print("Template DIRS =", [str(p) for p in TEMPLATES[0]['DIRS']])

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
DEFAULT_FROM_EMAIL = 'no-reply@cim.local'

# Where to redirect after login
LOGIN_REDIRECT_URL = 'main:user_map'
LOGOUT_REDIRECT_URL = 'main:home'
LOGIN_URL = 'main:login'