"""
Django settings for student_management_system project.

Generated by 'django-admin startproject' using Django 3.0.6.

For more information on this file, see
https://docs.djangoproject.com/en/3.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.0/ref/settings/
"""

import os
# from decouple import config


# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'kth8b3%_v)bp0br%0*06rsxx(x*e(d7zrd--%m9u^6erj-)=@3'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True
# DEBUG = os.environ.get('DJANGO_DEBUG', '') != 'False'



ALLOWED_HOSTS = ['midwesternuniversity.herokuapp.com',
                '127.0.0.1',
                'localhost',
                '103.90.84.50', 
                'mis.gci.edu.np',
                '103.90.84.50:8050',
                'demomis.gci.edu.np']

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    #local_apps
    'student_management_app',
    'school_apps.attendance.apps.AttendanceConfig',
    'school_apps.school_settings.apps.SchoolSettingsConfig',
    'school_apps.role_permission.apps.RolePermissionConfig',
    'school_apps.user_profile.apps.UserProfileConfig',
    'school_apps.transports.apps.TransportsConfig',
    'school_apps.announcement.apps.AnnouncementConfig',
    'school_apps.academic.apps.AcademicConfig',
    'school_apps.student.apps.StudentsConfig',
    'school_apps.teacher.apps.TeachersConfig',
    'school_apps.courses.apps.CoursesConfig',
    'school_apps.parents.apps.ParentsConfig',
    'school_apps.admin_user.apps.AdminUserConfig',
       'viewer.apps.ViewerConfig',
     'school_apps.exam.apps.ExamConfig',
    'school_apps.enquiry.apps.EnquiryConfig',
    'school_apps.visitor.apps.VisitorConfig',
     'school_apps.extrausers.apps.ExtrausersConfig',
    'school_apps.notifications.apps.NotificationsConfig',
     'school_apps.administrator.apps.AdministratorConfig',
    'school_apps.customusers.apps.CustomusersConfig',
    'school_apps.inventory.apps.InventoryConfig',
    'school_apps.ticket.apps.TicketConfig',
    'school_apps.spis.apps.SpisConfig',
    'school_apps.residential_management_system.apps.ResidentialManagementSystemConfig',
    'school_apps.cafeteria.apps.CafeteriaConfig',
    'school_apps.lms.apps.LmsConfig',
    'school_apps.events.apps.EventsConfig',
    'school_apps.logs.apps.LogsConfig',

    #~~~~~~~~~~~~~~~~~~api~~~~~~~~~~~~~~~~~~~~
    'school_apps.formapi.apps.FormapiConfig',

    #-----------third_party--------------'
    
    'crispy_forms',
    'crispy_bootstrap4',
    'django_countries',
    # 'django_filters',
    'debug_toolbar',
    'ckeditor',
    # 'django_extensions',
    # 'import_export',
    # 'simple_history',
    'schedule',
    # 'djangobower',
    # 'dbbackup',
    # 'widget_tweaks',
    # 'mathfilters',
    # 'webcam',
    'rest_framework',
    'corsheaders',
    'rest_framework.authtoken',
    'rest_framework_datatables',
    # 'django_dramatiq',
    # 'django_user_agents',
    # 'dramatiq'
]

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
    ],

    'DEFAULT_PERMISSION_CLASSES':[
        'rest_framework.permissions.IsAuthenticated',
    ],

    'DEFAULT_FILTER_BACKENDS': ['django_filters.rest_framework.DjangoFilterBackend'],
    
}


MIDDLEWARE = [
     'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'debug_toolbar.middleware.DebugToolbarMiddleware',#django debug
    # 'whitenoise.middleware.WhiteNoiseMiddleware',  #for heroku
    'simple_history.middleware.HistoryRequestMiddleware',#for simple history
    'school_apps.user_profile.middleware.LoginRequiredMiddleware',
    'school_apps.logs.middleware.UserLoggingMiddleware',
    # 'django_user_agents.middleware.UserAgentMiddleware',
]

# SESSION_ENGINE =[
#     'django.contrib.sessions.backends.signed_cookies'
# ]

CORS_ORIGIN_WHITELIST = [
    'http://192.168.43.243',
    'http://192.168.43.219',
]

CORS_ORIGIN_ALLOW_ALL = True

ALLOWED_HOSTS = [
    '192.168.43.243',
    '192.168.43.219',
    'localhost', 
    '127.0.0.1',
    'mangosoftsolution.com',
    'demomis.gci.edu.np',
]
ROOT_URLCONF = 'student_management_system.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR,'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
        #  'loaders': [
        #     ('django.template.loaders.cached.Loader', [
        #         'django.template.loaders.filesystem.Loader',
        #         'django.template.loaders.app_directories.Loader',
        #         'path.to.custom.Loader',
        #     ]),
        # ],
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                
                # for notification 
                'school_apps.notifications.context_processors.notifications_data',
                #for calendar link to sidebar
                # 'schedule.context_processors.fullcalendar_link',
                
                #for dyanamic settings footer and others
                # 'school_apps.school_settings.context_processors.settings_detail',
                
            ],
        },
    },
]


WSGI_APPLICATION = 'student_management_system.wsgi.application'


# Database
# https://docs.djangoproject.com/en/3.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
      
    }
}



# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.postgresql',
    
#         # 'NAME': 'gci_mis',
#         # 'USER': 'gci_mis',

#         'NAME': 'gci_mis_staging',
#         'USER': 'gci_mis_staging_user',
#         'PASSWORD': 'Nepal.123',
#         'HOST': '127.0.0.1',
#         'PORT': '5432',
#     }
# }


# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.postgresql',
    
#         # 'NAME': 'gci_mis',
#         # 'USER': 'gci_mis',

#         'NAME': 'gci_mis2',
#         'USER': 'gci_mis2',
#         'PASSWORD': 'Nepal.123',
#         'HOST': '127.0.0.1',
#         'PORT': '5432',
#     }
# }



# https://docs.djangoproject.com/en/3.0/ref/settings/#auth-password-validators

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


# Internationalization
# https://docs.djangoproject.com/en/3.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Asia/Kathmandu'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# rest framework
REST_FRAMEWORK = {
    # 'DEFAULT_SCHEMA_CLASS': 'rest_framework.schemas.coreapi.AutoSchema',
    # 'DATETIME_FORMAT': "%m/%d/%Y %H:%M:%S",
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.TokenAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ),
    'DEFAULT_PERMISSIONS_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',
        'rest_framework_datatables.renderers.DatatablesRenderer',
    ),
    'DEFAULT_FILTER_BACKENDS': (
        'rest_framework_datatables.filters.DatatablesFilterBackend',
    ),
    'DEFAULT_PAGINATION_CLASS': 'rest_framework_datatables.pagination.DatatablesPageNumberPagination',
    'DATETIME_FORMAT': "%Y-%m-%d %H:%M:%S",
}

# https://docs.djangoproject.com/en/3.0/howto/static-files/

STATICFILES_FINDERS = [
    #django schedular
'djangobower.finders.BowerFinder',

# #for staticfiles_dirs
 'django.contrib.staticfiles.finders.FileSystemFinder',
 'django.contrib.staticfiles.finders.AppDirectoriesFinder',
#   'compressor.finders.CompressorFinder',
#  'django.contrib.staticfiles.finders.DefaultStorageFinder',

]

BOWER_COMPONENTS_ROOT = os.path.join(BASE_DIR, 'static/calendar_static')


BOWER_INSTALLED_APPS = (
    'jquery',
    'jquery-ui',
    'bootstrap'
)

AUTH_USER_MODEL = "student_management_app.CustomUser"

STATIC_URL = '/static/'

STATICFILES_DIRS = [
    os.path.join(BASE_DIR,'static')
    ]

# when using collectstatic use static_root
STATIC_ROOT = os.path.join(BASE_DIR,'staticfiles')

# STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'#for heroku




MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR,'media/')
CRISPY_TEMPLATE_PACK = 'bootstrap4'


# AUTHENTICATION_BACKENDS=[
#     # 'student_management_app.views.EmailAuth.EmailBackEnd',#for login with email 
#     'django.contrib.auth.backends.ModelBackend'
#     ]

LOGIN_URL = '/accounts/login/'
LOGIN_REDIRECT_URL = '/home/'
LOGIN_EXEMPT_URLS = (
    r'^logout/$',
    r'^password/reset/.*$',
    r'^reset/.*$',
    r'^enquiry/enquiry_students/api/*$',
    # r'^api/*$',
    # r'^api/students/*$',
)


EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'nirmalpandey27450112@gmail.com'
EMAIL_HOST_PASSWORD = 'xrevudfkvavqwksx'
# DEFAULT_FROM_EMAIL = 'TestSite Team <noreply@example.com>'


DRAMATIQ_BROKER = {
    "BROKER": "dramatiq.brokers.redis.RedisBroker",
    "OPTIONS": {
        "url": "redis://localhost:6379",
    },
    "MIDDLEWARE": [
        "dramatiq.middleware.Prometheus",
        "dramatiq.middleware.AgeLimit",
        "dramatiq.middleware.TimeLimit",
        "dramatiq.middleware.Callbacks",
        "dramatiq.middleware.Retries",
        "django_dramatiq.middleware.DbConnectionsMiddleware",
        "django_dramatiq.middleware.AdminMiddleware",
    ]
}
# Defines which database should be used to persist Task objects when the
# AdminMiddleware is enabled.  The default value is "default".
DRAMATIQ_TASKS_DATABASE = "default"

DRAMATIQ_RESULT_BACKEND = {
    "BACKEND": "dramatiq.results.backends.redis.RedisBackend",
    "BACKEND_OPTIONS": {
        "url": "redis://localhost:6379",
    },
    "MIDDLEWARE_OPTIONS": {
        "result_ttl": 60000
    }
}

CKEDITOR_CONFIGS = {
    'default': {
        # 'toolbar': 'full',
        'height': 100,
        'width': 500,
        
        'toolbar': 'Custom',
        
         'toolbar_Custom': [
         
             ['Format','Styles','FontSize', 'TextColor','BGColor','Bold','Italic','Underline','Strike',
             'NumberedList','BulletedList','Outdent','Indent','JustifyLeft','JustifyCenter','JustifyRight', 'Link', 'Unlink',],
         ],
        
    },
}

DBBACKUP_STORAGE = 'django.core.files.storage.FileSystemStorage'
DBBACKUP_STORAGE_OPTIONS = {'location': os.path.join(BASE_DIR,'dbbackup')}
#This remove field warning for django latest version

#This remove field warning gor django latest version

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
#for debug toolbar
# INTERNAL_IPS = [
#     # ...
#     '127.0.0.1',
#     # ...
# ]