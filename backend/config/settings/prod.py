# backend/config/settings/prod.py
from .base import *  # noqa

env = environ.Env()

SECRET_KEY = env("SECRET_KEY")
DEBUG = False

ALLOWED_HOSTS = env.list("ALLOWED_HOSTS", default=["localhost"])

DATABASES = {
    "default": env.db("DATABASE_URL")
}

if env("CLOUD_SQL_CONNECTION_NAME", default=None):
    DATABASES["default"]["HOST"] = f'/cloudsql/{env("CLOUD_SQL_CONNECTION_NAME")}'
    DATABASES["default"]["PORT"] = ""

# CORS - Configuración mejorada
CORS_ALLOWED_ORIGINS = env.list("CORS_ALLOWED_ORIGINS", default=[])
CSRF_TRUSTED_ORIGINS = env.list("CSRF_TRUSTED_ORIGINS", default=[])

# Si no hay orígenes configurados, usar los valores predeterminados para producción
if not CORS_ALLOWED_ORIGINS:
    CORS_ALLOWED_ORIGINS = [
        "https://vetlab-frontend-7574522149.us-central1.run.app",
        "https://vetlab-frontend.uc.r.appspot.com",
        "https://vetlab-frontend-wywxkt3ffa-uc.a.run.app",
    ]
    CSRF_TRUSTED_ORIGINS = CORS_ALLOWED_ORIGINS.copy()

# También permitir usando regex para mayor flexibilidad
CORS_ALLOWED_ORIGIN_REGEXES = [
    r"^https://vetlab-frontend-.*\.run\.app$",
    r"^https://vetlab-frontend-.*\.uc\.r\.appspot\.com$",
]

# Configuración adicional de CORS
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_METHODS = [
    'DELETE',
    'GET',
    'OPTIONS',
    'PATCH',
    'POST',
    'PUT',
]
CORS_ALLOW_HEADERS = [
    'accept',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
]

SECURE_SSL_REDIRECT = True
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

# Archivos media en Cloud Storage en producción
DEFAULT_FILE_STORAGE = "storages.backends.gcloud.GoogleCloudStorage"
GS_BUCKET_NAME = env("GS_BUCKET_NAME", default="")
GS_PROJECT_ID = env("GCP_PROJECT_ID", default="")

EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = env("EMAIL_HOST", default="")
EMAIL_PORT = env.int("EMAIL_PORT", default=587)
EMAIL_HOST_USER = env("EMAIL_HOST_USER", default="")
EMAIL_HOST_PASSWORD = env("EMAIL_HOST_PASSWORD", default="")
EMAIL_USE_TLS = True

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "json": {"format": '{"level": "%(levelname)s", "time": "%(asctime)s", "module": "%(module)s", "message": "%(message)s"}'}
    },
    "handlers": {
        "console": {"class": "logging.StreamHandler", "formatter": "json"},
    },
    "root": {"handlers": ["console"], "level": "WARNING"},
    "loggers": {
        "django": {"handlers": ["console"], "level": "INFO", "propagate": False},
    },
}