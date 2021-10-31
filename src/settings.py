from pathlib import Path
import os
from os.path import join
from django.core.exceptions import ImproperlyConfigured
from django.utils import timezone


def get_env_value(env_variable):
    try:
        return os.environ[env_variable]
    except KeyError:
        error_msg = "Set the {} environment variable".format(env_variable)
        raise ImproperlyConfigured(error_msg)


# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

STATIC_ROOT = join(BASE_DIR, "static")

STATIC_URL = "/static/"

LOCALE_PATHS = (join(BASE_DIR, "jwt_auth", "locale"),)


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = get_env_value("SECRET_KEY")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = get_env_value("DEBUG").lower() in {"true", "1"}

ALLOWED_HOSTS = get_env_value("ALLOWED_HOSTS").split(" ")

# Application definition

INSTALLED_APPS = [
    "user",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django_extensions",
    "rest_framework",
    "corsheaders",
    "jwt_auth",
    "celery_worker",
]

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "wsgi.application"


# Database
# https://docs.djangoproject.com/en/3.2/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "HOST": get_env_value("POSTGRES_HOST"),
        "NAME": get_env_value("POSTGRES_APP_DATABASE"),
        "PORT": get_env_value("POSTGRES_PORT"),
        "USER": get_env_value("POSTGRES_APP_USER"),
        "PASSWORD": get_env_value("POSTGRES_APP_PASSWORD"),
    }
}

# Password validation
# https://docs.djangoproject.com/en/3.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# Internationalization
# https://docs.djangoproject.com/en/3.2/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_L10N = True

USE_TZ = True

LANGUAGE_CODE = "en"

LANGUAGES = [("en", "English"), ("ru", "Russian")]

# Default primary key field type
# https://docs.djangoproject.com/en/3.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


REST_FRAMEWORK = {"NON_FIELD_ERRORS_KEY": "message"}


# Custom settings
FRONTEND_DOMAIN_NAME = get_env_value("FRONTEND_DOMAIN_NAME")

AUTH_USER_MODEL = "user.User"

CORS_ALLOW_CREDENTIALS = get_env_value("DEBUG").lower() in {"true", "1"}

CORS_ALLOWED_ORIGINS = get_env_value("CORS_ALLOWED_ORIGINS").split()


EMAIL_TOKEN_MAX_AGE_DAYS = timezone.timedelta(
    days=int(get_env_value("EMAIL_TOKEN_MAX_AGE_DAYS"))
)

EMAIL_USE_TLS = get_env_value("DEBUG").lower() in {"true", "1"}

EMAIL_HOST = get_env_value("EMAIL_HOST")

EMAIL_HOST_USER = get_env_value("EMAIL_HOST_USER")

EMAIL_HOST_PASSWORD = get_env_value("EMAIL_HOST_PASSWORD")

EMAIL_PORT = get_env_value("EMAIL_PORT")


CELERY_BROKER_URL = get_env_value("CELERY_BROKER")

CELERY_RESULT_BACKEND = get_env_value("CELERY_BROKER")


AUTH_REFRESH_MAX_AGE_SEC = timezone.timedelta(
    seconds=int(get_env_value("AUTH_REFRESH_MAX_AGE_SEC"))
)

AUTH_REFRESH_COOKIE_SALT = get_env_value("AUTH_REFRESH_COOKIE_SALT")

AUTH_REFRESH_COOKIE_SCOPE = get_env_value("AUTH_REFRESH_COOKIE_SCOPE")

AUTH_REFRESH_COOKIE_NAME = get_env_value("AUTH_REFRESH_COOKIE_NAME")

AUTH_ACCESS_MAX_AGE_SEC = timezone.timedelta(
    seconds=int(get_env_value("AUTH_ACCESS_MAX_AGE_SEC"))
)
AUTH_ACCESS_JWT_SIGNING_KEY = get_env_value("AUTH_ACCESS_JWT_SIGNING_KEY")

AUTH_ACCESS_COOKIE_SCOPE = get_env_value("AUTH_ACCESS_COOKIE_SCOPE")

AUTH_ACCESS_COOKIE_NAME = get_env_value("AUTH_ACCESS_COOKIE_NAME")


RESET_PASSWORD_TOKEN_MAX_AGE_DAYS = timezone.timedelta(
    days=int(get_env_value("RESET_PASSWORD_TOKEN_MAX_AGE_DAYS"))
)


FRONTEND_CONFIRM_EMAIL_URL = get_env_value("FRONTEND_CONFIRM_EMAIL_URL")

FRONTEND_RESET_PASSWORD_URL = get_env_value("FRONTEND_RESET_PASSWORD_URL")
