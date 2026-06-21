from .base import *  # noqa
from .base import BASE_DIR

SECRET_KEY = "test-secret-key-not-for-production"
DEBUG = False

ALLOWED_HOSTS = ["*"]

# SQLite en memoria — tests rápidos, sin necesidad de Postgres real
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}

# Desactiva migraciones lentas, Django crea las tablas directo del modelo
class DisableMigrations:
    def __contains__(self, item):
        return True
    def __getitem__(self, item):
        return None

MIGRATION_MODULES = DisableMigrations()

PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.MD5PasswordHasher",  # más rápido para tests, NUNCA en prod
]

CORS_ALLOW_ALL_ORIGINS = True

EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"

# Sin whitenoise/static collection en tests
STATICFILES_STORAGE = "django.contrib.staticfiles.storage.StaticFilesStorage"