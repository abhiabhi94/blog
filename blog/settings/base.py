
import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))))

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'Blog.apps.BlogConfig',
    'Users.apps.UsersConfig',
    'Subscribers.apps.SubscribersConfig',
    'crispy_forms',
    'markupfield',
    'meta',
    'ckeditor',
    'ckeditor_uploader',
    'hitcount',
    'taggit',
    'taggit_autosuggest',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'blog.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
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

WSGI_APPLICATION = 'blog.wsgi.application'

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

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Asia/Kolkata'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.2/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'assets')

MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
MEDIA_URL = '/media/'

############# CKEditor specifications #####################


def get_plugin_meta(plugin, plugin_dir, plugin_file='plugin.js'):
    """ format for specifying plugin resources:
        (name of plugin,  
        'specific path to directory containing plugin.js', 
        'plugin.js')'"""
    plugin_base_dir = '/static/Blog/ckeditor_plugins/'
    return (plugin, os.path.join(plugin_base_dir, plugin_dir) + os.path.sep, plugin_file)


# CKEditor needs to know where its assets are located because it loads them lazily only when needed
CKEDITOR_BASEPATH = STATIC_URL + 'ckeditor/ckeditor/'
# This setting specifies a relative path to your CKEditor media upload directory
CKEDITOR_UPLOAD_PATH = 'blog/'
# This restricts access to uploaded images to the uploading user
# (e.g. each user only sees and uploads their own images)
CKEDITOR_RESTRICT_BY_USER = True
# enables image grouping by directory they are stored in, sorted by date.
CKEDITOR_BROWSE_SHOW_DIRS = True
# to convert and compress the uploaded images to jpeg, to save disk space
CKEDITOR_IMAGE_BACKEND = 'pillow'
CKEDITOR_FORCE_JPEG_COMPRESSION = True
CKEDITOR_IMAGE_QUALITY = 75
# To restrict upload functionality to image files only
CKEDITOR_ALLOW_NONIMAGE_FILES = False
# CKEditor configurations
CKEDITOR_CONFIGS = {
    'default': {
        # 'skin': 'moono',
        'width': '100%',
        # 'skin': 'office2013',
        'toolbar_Basic': [
            ['Source', '-', 'Bold', 'Italic']
        ],
        'toolbar_YourCustomToolbarConfig': [
            {'name': 'document', 'items': [
                'Source', '-', 'Save', 'Preview', '-', 'Templates']},
            {'name': 'clipboard', 'items': [
                'Cut', 'Copy', 'Paste', 'PasteText', 'PasteFromWord', '-', 'Undo', 'Redo']},
            {'name': 'editing', 'items': [
                'Find', 'Replace', '-', 'SelectAll']},
            # {'name': 'forms',
            #  'items': ['Form', 'Checkbox', 'Radio', 'TextField', 'Textarea', 'Select', 'Button', 'ImageButton',
            #            'HiddenField']},
            '/',
            {'name': 'basicstyles',
             'items': ['Bold', 'Italic', 'Underline', 'Strike', 'Subscript', 'Superscript', '-', 'RemoveFormat']},
            {'name': 'paragraph',
             'items': ['NumberedList', 'BulletedList', '-', 'Outdent', 'Indent', '-', 'Blockquote', 'CreateDiv', '-',
                       'JustifyLeft', 'JustifyCenter', 'JustifyRight', 'JustifyBlock', '-', 'BidiLtr', 'BidiRtl',
                       'Language']},
            {'name': 'links', 'items': ['Link', 'Unlink', 'Anchor']},
            {'name': 'insert',
             'items': ['Flash', 'Table', 'HorizontalRule', 'Smiley', 'SpecialChar', 'PageBreak', 'Iframe']},
            '/',
            {'name': 'styles', 'items': [
                'Styles', 'Format', 'Font', 'FontSize']},
            {'name': 'colors', 'items': ['TextColor', 'BGColor']},
            {'name': 'tools', 'items': ['Maximize', 'ShowBlocks']},
            {'name': 'about', 'items': ['About']},
            '/',  # put this to force next toolbar on new line
            {'name': 'yourcustomtools', 'items': [
                'Image',
                'CodeSnippet',
                'Youtube',
                # 'Templates'
                # put the name of your editor.ui.addButton here
                # 'Maximize',

            ]},
        ],
        'toolbar': 'YourCustomToolbarConfig',  # put selected toolbar config here
        'tabSpaces': 4,
        'extraPlugins': ','.join([
            'uploadimage',  # the upload image feature
            # your extra plugins here
            'codesnippet',
            'image2',
            'youtube',
            # 'templates'
        ]),
        'external_plugin_resources':
            [
                get_plugin_meta('youtube', 'youtube/youtube'),
                # get_plugin_meta('templates', 'templates')
        ],
        'youtube_resposive': 'true',
        'youtube_related': 'true',
        'youtube_controls': 'true',
    }
}

##########################

#### HITCOUNT APP ######

# This is the number of days, weeks, months, hours, etc(using a timedelta keyword argument), that an Hit is kept active
HITCOUNT_KEEP_HIT_ACTIVE = {'seconds': 1}
# Limit the number of active Hits from a single IP address. 0 means that it is unlimited
HITCOUNT_HITS_PER_IP_LIMIT = 0
# Exclude Hits from all users in the specified user groups
HITCOUNT_EXCLUDE_USER_GROUP = ('editor', )


CRISPY_TEMPLATE_PACK = 'bootstrap4'

LOGIN_REDIRECT_URL = 'Blog:home'
LOGIN_URL = 'login'

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True

### Used by Django-Meta app for rendering meta tags ###
META_USE_TITLE_TAG = True
META_USE_TWITTER_PROPERTIES = True
META_USE_OG_PROPERTIES = True
META_SITE_DOMAIN = 'hackadda.com'
META_SITE_PROTOCOL = 'https'
##########################################

# Django-taggit
TAGGIT_CASE_INSENSITIVE = True
