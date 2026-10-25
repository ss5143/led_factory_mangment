
"""
Django settings for LED Factory
"""

from pathlib import Path
import os
import sys


# =========================================================
# BASE DIRECTORY
# =========================================================

BASE_DIR = Path(__file__).resolve().parent.parent


# =========================================================
# PYINSTALLER DIRECTORY
# =========================================================

if getattr(sys, "frozen", False):
    # Files bundled inside PyInstaller
    BUNDLE_DIR = Path(sys._MEIPASS)

    # Writable permanent data location
    DATA_DIR = Path(
        os.environ.get(
            "PROGRAMDATA",
            r"C:\ProgramData"
        )
    ) / "LED Factory"

else:
    BUNDLE_DIR = BASE_DIR
    DATA_DIR = BASE_DIR


# =========================================================
# CREATE DATA DIRECTORIES
# =========================================================

DATA_DIR.mkdir(
    parents=True,
    exist_ok=True
)

# =========================================================
# SECURITY
# =========================================================

DEBUG = os.environ.get("DJANGO_DEBUG", "True").lower() in (
    "1", "true", "yes"
)

SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY")

if not SECRET_KEY:
    if DEBUG:
        SECRET_KEY = "local-development-only-change-before-deploy"
    else:
        raise RuntimeError(
            "DJANGO_SECRET_KEY must be set for production."
        )

ALLOWED_HOSTS = [
    host.strip()
    for host in os.environ.get(
        "DJANGO_ALLOWED_HOSTS",
        "127.0.0.1,localhost"
    ).split(",")
    if host.strip()
]
CSRF_TRUSTED_ORIGINS = [
    origin.strip()
    for origin in os.environ.get(
        "DJANGO_CSRF_TRUSTED_ORIGINS", ""
    ).split(",")
    if origin.strip()
]

# HTTPS security settings
SECURE_SSL_REDIRECT = (
    os.environ.get("DJANGO_SECURE_SSL_REDIRECT", "False").lower()
    in ("1", "true", "yes")
)

SESSION_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_SECURE = not DEBUG

SECURE_HSTS_SECONDS = (
    int(os.environ.get("DJANGO_SECURE_HSTS_SECONDS", "0"))
    if not DEBUG else 0
)

# =========================================================
# APPLICATIONS
# =========================================================

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "allauth",
    "allauth.account",
    "allauth.socialaccount",
    "allauth.socialaccount.providers.google",

    "accounts",
    "products",
    "orders",
    "purchases",
    "suppliers",
    "sales",
    "customers",
    "reports",
    "company",
]


# =========================================================
# MIDDLEWARE
# =========================================================

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "allauth.account.middleware.AccountMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
]


# =========================================================
# URL
# =========================================================

ROOT_URLCONF = "led_factory.urls"


# =========================================================
# TEMPLATES
# =========================================================

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",

        "DIRS": [
            BUNDLE_DIR / "templates",
        ],

        "APP_DIRS": True,

        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]


# =========================================================
# WSGI
# =========================================================

WSGI_APPLICATION = "led_factory.wsgi.application"

# =========================================================
# DATABASE
# =========================================================

DATABASE_PATH = DATA_DIR / "db.sqlite3"

DATABASE_URL = os.environ.get("DATABASE_URL")

if DATABASE_URL:
    import dj_database_url

    DATABASES = {
        "default": dj_database_url.parse(
            DATABASE_URL,
            conn_max_age=600,
            ssl_require=not DEBUG,
        )
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": DATABASE_PATH,
        }
    }




# =========================================================
# STATIC FILES
# =========================================================

STATIC_URL = "/static/"


if getattr(sys, "frozen", False):

    # Read bundled CSS/JS/images from PyInstaller
    STATICFILES_DIRS = [
        BUNDLE_DIR / "static",
    ]

else:

    STATICFILES_DIRS = [
        BASE_DIR / "static",
    ]


# IMPORTANT:
# Never use Program Files or _internal for writing static files

STATIC_ROOT = DATA_DIR / "staticfiles"

STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedStaticFilesStorage",
    },
}


# =========================================================
# MEDIA FILES
# =========================================================

MEDIA_URL = "/media/"

MEDIA_ROOT = DATA_DIR / "media"

MEDIA_ROOT.mkdir(
    parents=True,
    exist_ok=True
)


# =========================================================
# PASSWORD VALIDATION
# =========================================================

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME":
            "django.contrib.auth.password_validation."
            "UserAttributeSimilarityValidator",
    },
    {
        "NAME":
            "django.contrib.auth.password_validation."
            "MinimumLengthValidator",
    },
    {
        "NAME":
            "django.contrib.auth.password_validation."
            "CommonPasswordValidator",
    },
    {
        "NAME":
            "django.contrib.auth.password_validation."
            "NumericPasswordValidator",
    },
]


# =========================================================
# LANGUAGE / TIME
# =========================================================

LANGUAGE_CODE = "en-us"

TIME_ZONE = "Asia/Karachi"

USE_I18N = True

USE_TZ = True


# =========================================================
# DEFAULT PRIMARY KEY
# =========================================================

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


# Keep standard username/password login and enable Allauth.
AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
    "allauth.account.auth_backends.AuthenticationBackend",
]


# Google OAuth credentials must be supplied through environment variables.
SOCIALACCOUNT_PROVIDERS = {
    "google": {
        "APP": {
            "client_id": os.environ.get("GOOGLE_CLIENT_ID", ""),
            "secret": os.environ.get("GOOGLE_CLIENT_SECRET", ""),
            "key": "",
        },
        "SCOPE": ["profile", "email"],
    },
}


# Google OAuth / django-allauth
ACCOUNT_EMAIL_VERIFICATION = "none"
SOCIALACCOUNT_AUTO_SIGNUP = True
SOCIALACCOUNT_EMAIL_VERIFICATION = "none"
LOGIN_REDIRECT_URL = "/"
