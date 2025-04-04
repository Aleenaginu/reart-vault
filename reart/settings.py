"""
Django settings for reart project.

Generated by 'django-admin startproject' using Django 5.0.7.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.0/ref/settings/
"""
import os
from dotenv import load_dotenv 
from pathlib import Path
load_dotenv()

# GOOGLE_OAUTH_CLIENT_ID='467600298779-s09okfeii93d33mbkuf0vm87oepafvq8.apps.googleusercontent.com'

# GOOGLE_OAUTH_CLIENT_ID = os.getenv('467600298779-s09okfeii93d33mbkuf0vm87oepafvq8.apps.googleusercontent.com')
# GOOGLE_OAUTH_CLIENT_SECRET='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'
# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# GOOGLE_OAUTH_REDIRECT_URI = 'http://127.0.0.1:8000/auth-receiver/'
# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-ah(=!6a-hveva1elgo7npxy$k#&^nirroc4zoyqms@d6#73leq'
# SECRET_KEY = os.getenv('django-insecure-ah(=!6a-hveva1elgo7npxy$k#&^nirroc4zoyqms@d6#73leq')
# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True
SITE_ID = 1
ALLOWED_HOSTS = ['localhost', '127.0.0.1', 'reart-vault-169p.onrender.com']


# Application definition

INSTALLED_APPS = [
    'social_django',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.sites',
    'django.contrib.staticfiles',
    'accounts',
    'donors',
    'artist',
    'adminclick',
    'shop',
    'category',
    'cart',
    'delivery',
    'face_auth',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
 
]

ROOT_URLCONF = 'reart.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'template')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'social_django.context_processors.backends',
                'social_django.context_processors.login_redirect',
                'category.context_processors.menu_links',
                'cart.context_processors.counter',
                # 'shop.context_processors.wishlist_count',
            ],
        },
    },
]

WSGI_APPLICATION = 'reart.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases

# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.sqlite3',
#         'NAME': BASE_DIR / 'db.sqlite3',
#     }
# }
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / "db.sqlite3",
        'OPTIONS': {
            'timeout': 30,  # Increased timeout
            'isolation_level': None,  # This will help with concurrent access
        },
    }
}


# Password validation
# https://docs.djangoproject.com/en/5.0/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/5.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.0/howto/static-files/

STATIC_URL = 'static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_DIRS=[os.path.join(BASE_DIR,'static')]
STATICFILES_STORAGE = 'whitenoise.storage.CompressedStaticFilesStorage'

MEDIA_URL= 'media/'
MEDIA_ROOT= os.path.join(BASE_DIR,'media')

# WhiteNoise Configuration
WHITENOISE_MANIFEST_STRICT = False
WHITENOISE_USE_FINDERS = True

# Default primary key field type
# https://docs.djangoproject.com/en/5.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'reartvault@gmail.com'
EMAIL_HOST_PASSWORD = 'cdpt ofwa owyy bhoj'
DEFAULT_FROM_EMAIL = 'webmaster@localhost'


from django.contrib.messages import constants as messages

MESSAGE_TAGS = {
    messages.DEBUG: 'debug',
    messages.INFO: 'info',
    messages.SUCCESS: 'success',
    messages.WARNING: 'warning',
    messages.ERROR: 'error',
}

AUTHENTICATION_BACKENDS = (
    'social_core.backends.google.GoogleOAuth2',
    'django.contrib.auth.backends.ModelBackend',
)

# Add social auth settings
SOCIAL_AUTH_GOOGLE_OAUTH2_KEY = '467600298779-s09okfeii93d33mbkuf0vm87oepafvq8.apps.googleusercontent.com'
SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET = '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'

# Gemini API Configuration
GEMINI_API_KEY = 'AIzaSyAX0vpRqWM-YXaDyXv2K_ZLYhiPX5lxKXI'  # Replace with your actual Gemini API key

LOGIN_URL = 'userlogin'
LOGOUT_URL = 'userlogout'
LOGIN_REDIRECT_URL = 'shop_index'
LOGOUT_REDIRECT_URL = '/'

# Add Social Auth pipeline (optional)
SOCIAL_AUTH_PIPELINE = (
    'social_core.pipeline.social_auth.social_details',
    'social_core.pipeline.social_auth.social_uid',
    'social_core.pipeline.social_auth.auth_allowed',
    'social_core.pipeline.social_auth.social_user',
    'social_core.pipeline.user.get_username',
    'social_core.pipeline.user.create_user',
    'accounts.pipeline.set_user_role',
    'social_core.pipeline.social_auth.associate_user',
    'social_core.pipeline.social_auth.load_extra_data',
    'social_core.pipeline.user.user_details',
)


# RAZORPAY_API_KEY = 'rzp_test_zXqniu2WbyToOX'
# RAZORPAY_API_SECRET_KEY = 'PqqXMqDJViYcLlIocc65V9m4'
RAZORPAY_API_KEY = 'rzp_test_Q16TA7WvW93Ile'
RAZORPAY_API_SECRET_KEY = 'kDbKUnWN7G9LQTznXOXMIPv5'
CSRF_TRUSTED_ORIGINS = ['https://api.razorpay.com']
