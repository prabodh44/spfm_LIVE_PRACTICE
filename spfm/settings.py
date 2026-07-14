"""
Django settings for spfm project.

Changed the file for production. 

What changes have be done and 
why is recorded in the google document

"""

import os
from pathlib import Path

import dj_database_url
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")


def env(key, default=""):
    return os.environ.get(key, default)


# SECURITY WARNING: keep the secret key used in production secret!
# In production this MUST come from an environment variable / .env file.
SECRET_KEY = env(
    "DJANGO_SECRET_KEY",
    "django-insecure-c0nw1p65)v&+^ro8#!&d0_i0kzsvpr_49r#p97spd=6vd#7max",
)

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env("DJANGO_DEBUG", "True") == "True"

ALLOWED_HOSTS = [h.strip() for h in env("DJANGO_ALLOWED_HOSTS", "localhost,127.0.0.1").split(",") if h.strip()]

# Full origins (with scheme) that are trusted to POST to this site — required
# by Django for CSRF checks whenever the site is reached over HTTPS, or from
# a domain that doesn't match a plain host header check. Example value:
# "https://example.com,http://165.22.1.1"
CSRF_TRUSTED_ORIGINS = [h.strip() for h in env("DJANGO_CSRF_TRUSTED_ORIGINS", "").split(",") if h.strip()]


# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "core",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "spfm.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "core.context_processors.site_info",
            ],
        },
    },
]

WSGI_APPLICATION = "spfm.wsgi.application"


# Database
# Uses SQLite by default (zero setup) for local development.
# Set DATABASE_URL in production to switch to Postgres automatically, e.g.:
#   DATABASE_URL=postgres://myprojectuser:changeme@localhost:5432/myproject

DATABASE_URL = env("DATABASE_URL", "")

if DATABASE_URL:
    DATABASES = {
        "default": dj_database_url.parse(DATABASE_URL, conn_max_age=600)
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }


# Password validation

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]


# Internationalization

LANGUAGE_CODE = "en-au"
TIME_ZONE = "Australia/Sydney"
USE_I18N = True
USE_TZ = True


# Static & media files

STATIC_URL = "static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"
STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {
        "BACKEND": (
            "django.contrib.staticfiles.storage.StaticFilesStorage"
            if DEBUG
            else "whitenoise.storage.CompressedManifestStaticFilesStorage"
        )
    },
}

MEDIA_URL = "media/"
MEDIA_ROOT = BASE_DIR / "media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


# --------------------------------------------------------------------------
# Business / site settings
# --------------------------------------------------------------------------

SITE_NAME = "SP Facilities Management"
SITE_TAGLINE = "Clean Spaces. Better Places."
BUSINESS_PHONE = env("BUSINESS_PHONE", "1300 000 000")
BUSINESS_PHONE_TEL = env("BUSINESS_PHONE_TEL", "+611300000000")
BUSINESS_EMAIL = env("BUSINESS_EMAIL", "info@spfacilitiesmgmt.com.au")
BUSINESS_ADDRESS = env("BUSINESS_ADDRESS", "Suite 4, 120 Example Street, Sydney NSW 2000")
BUSINESS_MAP_EMBED_SRC = env(
    "BUSINESS_MAP_EMBED_SRC",
    "https://www.google.com/maps?q=Sydney%20NSW&output=embed",
)


# --------------------------------------------------------------------------
# Email (used to notify the owner of new quote requests / enquiries)
# --------------------------------------------------------------------------
# In development, emails print to the console instead of actually sending.
# To send real emails in production, set DJANGO_EMAIL_BACKEND=smtp and fill
# in the EMAIL_* variables in your .env file.

if env("DJANGO_EMAIL_BACKEND", "console") == "smtp":
    EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
    EMAIL_HOST = env("EMAIL_HOST", "smtp.gmail.com")
    EMAIL_PORT = int(env("EMAIL_PORT", "587"))
    EMAIL_USE_TLS = env("EMAIL_USE_TLS", "True") == "True"
    EMAIL_HOST_USER = env("EMAIL_HOST_USER")
    EMAIL_HOST_PASSWORD = env("EMAIL_HOST_PASSWORD")
else:
    EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

DEFAULT_FROM_EMAIL = env("DEFAULT_FROM_EMAIL", "website@spfacilitiesmgmt.com.au")

# Where new lead notifications are sent (the business owner's inbox).
OWNER_NOTIFICATION_EMAIL = env("OWNER_NOTIFICATION_EMAIL", BUSINESS_EMAIL)


# --------------------------------------------------------------------------
# SMS (optional, via Twilio) - see core/notifications.py for details.
# Leave blank to skip SMS notifications entirely (email still works).
# --------------------------------------------------------------------------

TWILIO_ACCOUNT_SID = env("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = env("TWILIO_AUTH_TOKEN")
TWILIO_FROM_NUMBER = env("TWILIO_FROM_NUMBER")
OWNER_SMS_NUMBER = env("OWNER_SMS_NUMBER")


# --------------------------------------------------------------------------
# Security (tightened automatically when DEBUG=False)
# --------------------------------------------------------------------------
# IMPORTANT: keep DJANGO_USE_HTTPS=False until Certbot/HTTPS is actually
# working on your domain. Let's Encrypt cannot issue a certificate for a
# bare IP address, so if you flip this True before you have a real domain
# with HTTPS configured, your site will redirect-loop and become unreachable.

USE_HTTPS = env("DJANGO_USE_HTTPS", "True") == "True"

if not DEBUG:
    SECURE_SSL_REDIRECT = USE_HTTPS
    SESSION_COOKIE_SECURE = USE_HTTPS
    CSRF_COOKIE_SECURE = USE_HTTPS
    SECURE_HSTS_SECONDS = 31536000 if USE_HTTPS else 0
    SECURE_HSTS_INCLUDE_SUBDOMAINS = USE_HTTPS
    SECURE_HSTS_PRELOAD = USE_HTTPS
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    X_FRAME_OPTIONS = "DENY"