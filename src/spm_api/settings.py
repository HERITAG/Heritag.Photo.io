"""
Django settings for SimplePhotoManagement project.
"""
import os
import string
import random
""" INITIAL PARAMETERS """

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_UPLOAD_MAX_NUMBER_FIELDS = 10240  # higher than the count of fields
DEBUG = int(os.environ.get('DEBUG', default=0))
# # # GENERATE A NEW UNIQUE SECRET KEY (secret_key.txt) IF DOES NOT ALREADY EXIST
KEY_PATH = os.path.join(BASE_DIR, 'secret_key', 'secret_key.txt')
try:
    with open(KEY_PATH, 'r') as f:
        SECRET_KEY = f.read().strip()
except IOError:
    SECRET_KEY = ''.join([random.SystemRandom().choice(string.ascii_letters + string.digits + string.punctuation)
                          for _ in range(50)])
    with open(KEY_PATH, 'w') as f:
        f.write(SECRET_KEY)

""" MAIN CONFIGURATION """

# # # Network
APP_URL = os.environ.get('APP_URL', 'localhost')
ROOT_URLCONF = 'spm_api.urls'
WSGI_APPLICATION = 'spm_api.wsgi.application'
X_FRAME_OPTIONS = 'DENY'
# SECURE_HSTS_SECONDS = 3600
SECURE_CONTENT_TYPE_NOSNIFF = False
SECURE_BROWSER_XSS_FILTER = False
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False
ALLOWED_HOSTS = [APP_URL]
#CORS_ORIGIN_ALLOW_ALL = True
CORS_ALLOW_CREDENTIALS = True
CORS_ORIGIN_WHITELIST = (APP_URL, 'localhost')
STATIC_ROOT = os.path.join(BASE_DIR, 'static')
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# # # Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'spm_app.apps.SpmConfig',
    'rest_framework',
    'rest_framework.authtoken',
    'corsheaders',
    'django_q'
]

# # # Rest framework
REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'spm_app.custom_permissions.AccessPermissions',
    ],
    'PAGE_SIZE': 5,
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.LimitOffsetPagination',
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.TokenAuthentication',
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.BasicAuthentication',
    ),
    # 'DEFAULT_THROTTLE_CLASSES': (
    #     'rest_framework.throttling.AnonRateThrottle',
    #     'rest_framework.throttling.UserRateThrottle'
    # ),
    # 'DEFAULT_THROTTLE_RATES': {
    #     'anon': '1/second',
    #     'user': '2/second'
    # }
}

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.locale.LocaleMiddleware',
]

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
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

Q_CLUSTER = {
    'name': 'SimplePhotoManagement',
    'daemonize_workers': True,
    'compress': True,
    'workers': 2,
    'recycle': 5000,
    'timeout': None,
    # 'django_redis': 'default',
    'retry': 100000,
    'queue_limit': 4,
    'bulk': 1,
    'orm': 'default',
    'sync': False,  # Set True to debug in sync mode.
    'guard_cycle': 5,
    'cpu_affinity': 1,
    'catch_up': True
}

SPM = {
    'ORIGIN_IMAGE_PATHS': {os.environ.get('ORIGIN_IMAGE_PATH', default='/photo_directory')},
    'PROCESSED_IMAGE_PATH': os.environ.get('PROCESSED_IMAGE_PATH', default='/src/media/photos'),
    'PROCESSED_THUMBNAIL_PATH': os.environ.get('PROCESSED_TN_PATH', default='/src/media/photos_tn'),
    'PUBLIC_URL': os.environ.get('PUBLIC_PHOTO_URL', default='/media/photos'),
    'PUBLIC_URL_TN': os.environ.get('PUBLIC_PHOTO_TN_URL', default='/media/photos_tn'),
    'CONVERSION_FORMAT': os.environ.get('PHOTO_CONVERSION_FORMAT', default='.jpg'),
    'VALID_UPDATE_MODES': {'add_tags', 'remove_tag', 'rotate_image'},
    'THUMB_SIZES':  [(1080, 1080), (720, 720), (350, 350), (150, 150), (75, 75)]
}

# # # Caches
USE_REDIS_CACHE = False
# site-wide caching system. Set False for more granular control with view & template caching.
SITE_WIDE_CACHE = True
# 0 means equates to 'do not cache'. E.g. to cache for 24 hours: ((60 * 60) * 60) * 24
DEFAULT_CACHES_TTL = 0
CACHE_SESSION_SECONDS = 60 * 60

if SITE_WIDE_CACHE:
    CACHE_MIDDLEWARE_ALIAS = 'default'
    CACHE_MIDDLEWARE_SECONDS = DEFAULT_CACHES_TTL  # cache session data for an hour
    CACHE_MIDDLEWARE_KEY_PREFIX = 'simple_photo_management_production_server'
    # HAS TO GO FIRST IN MIDDLEWARE LIST
    MIDDLEWARE.insert(0, 'django.middleware.cache.UpdateCacheMiddleware')
    # HAS TO GO LAST IN MIDDLEWARE LIST
    MIDDLEWARE.append('django.middleware.cache.FetchFromCacheMiddleware')

if not USE_REDIS_CACHE:
    CACHES = {'default':
              {'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
               'TIMEOUT': DEFAULT_CACHES_TTL,
               'LOCATION': 'simple_photo_management-backend-cache'
               },
              'template_fragments':
                  {'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
                   'TIMEOUT': DEFAULT_CACHES_TTL,
                   'LOCATION': 'simple_photo_management-template-fragments-cache'
                   }
              }
else:
    CACHES = {
        'default': {
            'BACKEND': 'django_redis.cache.RedisCache',
            'LOCATION': 'redis://redis:6379/1',
            # default TTL for the cache in sects(e.g. 5 mins = 'TIMEOUT': 60 * 5)
            'TIMEOUT': DEFAULT_CACHES_TTL,
            'OPTIONS': {
                'CLIENT_CLASS': 'django_redis.client.DefaultClient'
            },
            'KEY_PREFIX': 'simple_photo_management_production_server'
        },
        'sessions': {  # used by SESSION_CACHE_ALIAS, below
            'BACKEND': 'django_redis.cache.RedisCache',
            'LOCATION': 'redis://redis:6379/3',
            'TIMEOUT': CACHE_SESSION_SECONDS,
            'OPTIONS': {
                'CLIENT_CLASS': 'django_redis.client.DefaultClient'
            },
            'KEY_PREFIX': 'simple_photo_management_production_server'
        },
        'template_fragments': {
            'BACKEND': 'django_redis.cache.RedisCache',
            'LOCATION': 'redis://redis:6379/4',
            'TIMEOUT': DEFAULT_CACHES_TTL,
            'OPTIONS': {
                'CLIENT_CLASS': 'django_redis.client.DefaultClient'
            },
            'KEY_PREFIX': 'simple_photo_management_production_server'
        },
    }

# # # Database
DATABASES = {
    'default': {
        'ENGINE': os.environ.get('SQL_ENGINE', 'django.db.backends.sqlite3'),
        'NAME': os.environ.get('SQL_DATABASE', os.path.join(BASE_DIR, 'db.sqlite3')),
        'USER': os.environ.get('SQL_USER', 'user'),
        'PASSWORD': os.environ.get('SQL_PASSWORD', 'password'),
        'HOST': os.environ.get('SQL_HOST', 'localhost'),
        'PORT': os.environ.get('SQL_PORT', '5432'),
    }
}

STATICFILES_DIRS = []  # extra static files dirs
STATIC_URL = '/static/'
MEDIA_URL = '/media/'
STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.ManifestStaticFilesStorage'

# # # Password validation
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

# # # Internationalization
LOCALE_PATHS = (
    os.path.join(BASE_DIR, 'locale'),
)
LANGUAGE_CODE = 'en-gb'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = True

# Logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s'
        },
        'simple': {
            'format': '%(asctime)s %(levelname)s %(message)s'
        }
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'simple'
        },
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': '/var/log/spm.log',
            'formatter': 'verbose'
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'INFO',
            'propagate': False,
        },
        'django_q': {
            'handlers': ['file'],
            'level': 'DEBUG',
            'propagate': True,
        },
    },
}
