# Django settings for MP100 project.
import os
import sys
from os.path import dirname
from celery.schedules import crontab
BASEDIR = dirname(__file__)
sys.path.append(BASEDIR+'/../deps/')
sys.path.append(BASEDIR+'/djangobb/')

#PRODUCTION UBUNTU
import djcelery
djcelery.setup_loader()
#BROKER_HOST = "mp100"
#BROKER_HOST = "ubuntu"
BROKER_HOST = "giussepi-desktop"
BROKER_PORT = 5672
BROKER_USER = "giussepi"
BROKER_PASSWORD = "1992"
BROKER_VHOST = "myvhost"
CELERYBEAT_SCHEDULE = {
    # Executes every Monday at 00:00
    "every-sunday-midnight":{
        "task":"fotos.tasks.weeklyTopAmbassadors",
        #"schedule":crontab(day_of_week=3),
        "schedule":crontab(hour=0, minute=0, day_of_week=1),
        }
    }
CELERYBEAT_SCHEDULER = "djcelery.schedulers.DatabaseScheduler"



site_name = 'MP100'
LOGIN_URL = '/'
#EMAIL_HOST = 'smtp.gmail.com'
#EMAIL_PORT = 587
#EMAIL_HOST_USER = 'YoEstuveEnMachuPicchu@gmail.com'
#EMAIL_HOST_PASSWORD= 'yoestuvetambienenmachupicchu'
POSTMARK_API_KEY    = '277e0595-6b40-4e44-a643-7d28b48ffe70'
POSTMARK_SENDER     = 'info@machu-picchu100.com'
POSTMARK_TEST_MODE  = False
#EMAIL_BACKEND = 'postmark.django_backend.EmailBackend'
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
EMAIL_USE_TLS = True
DEFAULT_FROM_EMAIL= 'info@machu-picchu100.com' #direccion por defecto de los mails enviados
#DEFAULT_FROM_EMAIL= 'MP100 <YoEstuveEnMachuPicchu@gmail.com>' #direccion por defecto de los mails enviados
AKISMET_API_KEY = 'c79b5f8bd209'
ZINNIA_AKISMET_COMMENT = False
ZINNIA_FEEDS_MAX_ITEMS = 6 #nro de entries que se muestran del zinnia
ZINNIA_PAGINATION = 2
BITLY_LOGIN = 'giussepi'
BITLY_API_KEY = 'R_5637f5d3f1c8d086797b5cf72ee67176'
TWITTER_CONSUMER_KEY = '0QV7AHCeyW38qdlvAEUv8A'
TWITTER_CONSUMER_SECRET = 'FLKtZCOAaSM3uPkinNdH5WIHB6dnvvOQIhV063GVE'
TWITTER_ACCESS_KEY = '238227055-mYT5cZ0KMyE8BeVCI8LfpgEFxETv16G8jQ2N3MQX'
TWITTER_ACCESS_SECRET = 'K4Re8DCnOWDfsynHlQUA6Y1PXqxd1Lkt7htLs1rrU'
RECAPTCHA_PUB_KEY = '6LdToMISAAAAALoEdKr9oYU3Xc-9mwl8UrdbUHv_'
RECAPTCHA_PRIVATE_KEY = '6LdToMISAAAAALQ8uZOOJKWSV6b6evjUoJXOHQY6'

SESSION_EXPIRE_AT_BROWSER_CLOSE=True
AUTH_PROFILE_MODULE = 'fotos.UserProfile'

DEBUG = True
TEMPLATE_DEBUG = DEBUG

#Change to true before deploying into production
ENABLE_SSL = False

ADMINS = (
     ('giussepi', 'giussepexy@gmail.com'),
)

MANAGERS = ADMINS

DATABASES = {
    'default': {
        #'ENGINE': 'django.db.backends.postgresql',
        'ENGINE': 'mysql', # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
#        'NAME': 'mp100_mp100',                      # Or path to database file if using sqlite3.
#        'USER': 'mp100',                      # Not used with sqlite3.
#        'PASSWORD': '123456',                  # Not used with sqlite3.
#        'HOST': 'postgresql.alwaysdata.com',                      # Set to empty string for localhost. Not used with sqlite3.
#        'PORT': '',                      # Set to empty string for default. Not used with sqlite3.
        #LUIS ESTA ES TU configuracion local
        #'ENGINE': 'django.db.backends.sqlite3', # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': 'mp100',                      # Or path to database file if using sqlite3.
        'USER': 'root',                      # Not used with sqlite3.
        'PASSWORD': 'abirato',                  # Not used with sqlite3.
        'HOST': 'localhost',                      # Set to empty string for localhost. Not used with sqlite3.
        #'PORT': '3306',                      # Set to empty string for default. Not used with sqlite3.
    }
}


# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# On Unix systems, a value of None will cause Django to use the same
# timezone as the operating system.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'America/Lima'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
#LANGUAGE_CODE = 'en-us'
LANGUAGE_CODE = 'es-pe'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale
USE_L10N = True


MEDIA_ROOT = '%s/public/media/' % BASEDIR

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
#MEDIA_URL = 'http://mymediafiles.com/'
MEDIA_URL = '/media/'
ZINNIA_MEDIA_URL = '%szinnia/' % MEDIA_URL
TINYMCE_JS_URL = '%s/js/tiny_mce/tiny_mce.js' % MEDIA_URL
TINYMCE_JS_ROOT = '%s/js/tiny_mce' % MEDIA_ROOT

#django-countries
COUNTRIES_FLAG_PATH = 'flags/%s.gif'

FLAG_PATH = '%sflags/' % MEDIA_URL

LOCALE_PATHS = '%s/locale/' % BASEDIR

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = '/media/adminmedia/media/'
#ADMIN_MEDIA_PREFIX = '/media/adminmedia/media/'

#variables para el upload_to
#USERPROFILE_PHOTO_PATH = 'C:/xampp/htdocs/MP100/public/media/images/usuarios/'
USERPROFILE_PHOTO_PATH = 'images/usuarios/perfil/'
USERPHOTOS_FOLDER_PATH = 'images/usuarios/fotos_concurso/'
BADGES_FOLDER_PATH = 'images/badges/'

# Make this unique, and don't share it with anybody.
SECRET_KEY = '0y!7pfrxc$&w$us2rcl(3j4!%&oel$4m$sewul&7_d)n@p@9w4'

# Endless Pagination
ENDLESS_PAGINATION_PER_PAGE = 10

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
#     'django.template.loaders.eggs.Loader',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'djangoprofilingmiddleware.ProfileMiddleware',
    'djangobb_forum.middleware.LastLoginMiddleware',
    'djangobb_forum.middleware.UsersOnline',

)

TEMPLATE_CONTEXT_PROCESSORS = (
    "django.contrib.auth.context_processors.auth",
    "django.core.context_processors.debug",
    "django.core.context_processors.i18n",
    "django.core.context_processors.media",
    "django.contrib.messages.context_processors.messages",
    "django.core.context_processors.request",
    'zinnia.context_processors.version',
    "zinnia.context_processors.media",
    'messages.context_processors.inbox',
    'djangobb_forum.context_processors.forum_settings',
)


ROOT_URLCONF = 'urls'

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    '%s/templates' % BASEDIR
    #"/home/mp100/MP100/templates/",
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.comments',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.admin',
    'django.contrib.sitemaps',
    'django.contrib.webdesign',
    'fotos',
    'portal',
    'countries',
    'admin',
    #'easy_thumbnails',
    'athumb',
    'watermarker',
    'ip2country',
    'tagging',
    'zinnia',
    'mptt',
    'django_bitly',
    'tweepy',
    'tinymce',
    'common',
#    'cloudfiles',
    'storages',
    'endless_pagination',
    'djangobb',
    'djangobb_forum',
    'registration',
    'haystack',
    'messages',
    'brabeion',
    'servicios',
    'djcelery',
    # Uncomment the next line to enable admin documentation:
    # 'django.contrib.admindocs',
)

if sys.argv[1] == 'test':
    GEO_SUPPORT = False
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3', # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
            'NAME': ':memory',
            'USER': '',                      # Not used with sqlite3.
            'PASSWORD': '',                  # Not used with sqlite3.
            'HOST': '',                      # Set to empty string for localhost. Not used with sqlite3.
            'PORT': '',                      # Set to empty string for default. Not used with sqlite3.
        }
    }

# MEDIA_URL = 'http://c567136.r36.cf2.rackcdn.com/'
# CLOUDFILES_USERNAME = 'quimerahg'
# CLOUDFILES_API_KEY = '255cc2ca1b45978a7cb4f4d01c931a14'
# CLOUDFILES_CONTAINER = 'test-container'
# CLOUDFILES_TTL = 72
# DEFAULT_FILE_STORAGE = 'storages.backends.mosso.ThreadSafeCloudFilesStorage'
# THUMBNAIL_DEFAULT_STORAGE = 'storages.backends.mosso.ThreadSafeCloudFilesStorage'

# CLOUDFILES_CONNECTION_KWARGS = {}
MEDIA_URL = 'http://s3.amazonaws.com/mp100pruebas/'
ADMIN_MEDIA_PREFIX =  MEDIA_URL+'adminmedia/media/'
DEFAULT_FILE_STORAGE = 'athumb.backends.s3boto.S3BotoStorage_AllPublic'
MEDIA_CACHE_BUSTER = '24-05-2011'
AWS_ACCESS_KEY_ID = 'AKIAJWECVMZXGDD2HIBA'
AWS_SECRET_ACCESS_KEY = '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'
AWS_STORAGE_BUCKET_NAME = 'mp100pruebas'
AWS_S3_CUSTOM_DOMAIN = 's3.amazonaws.com/mp100pruebas/'
WATERMARK_CACHE_TIMEOUT = sys.maxint
AWS_BOTO_FORCE_HTTP = True
AWS_S3_SECURE_URLS = False
AWS_QUERYSTRING_AUTH = False
AWS_HEADERS = {
  'Expires': 'Thu, 15 Apr 2015 20:00:00 GMT',  #<-- replace with whatever
  'Cache-Control': 'max-age=86400',     #<-- replace with whatever
 }
THUMBNAIL_DEBUG = True
S3_UPLOAD_URL = 'http://s3.amazonaws.com/mp100pruebas'

#HAYSTACK_SEARCH_ENGINE = 'whoosh'
#HAYSTACK_SITECONF = 'djangobb.search_sites'
import os
# HAYSTACK_CONNECTIONS = {
#     'default': {
#         # For Whoosh:
#         'ENGINE': 'haystack.backends.whoosh_backend.WhooshEngine',
#         'PATH':os.path.join(os.path.dirname(__file__),'djangobb/djangobb_index'),
#         'INCLUDE_SPELLING': True,
#     },
# }
HAYSTACK_SITECONF = 'search_sites'
HAYSTACK_SEARCH_ENGINE = 'whoosh'
HAYSTACK_WHOOSH_PATH = os.path.dirname(__file__) + '/search_index'

