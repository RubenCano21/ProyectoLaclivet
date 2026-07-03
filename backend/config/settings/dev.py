import environ
from .base import *  # noqa
from .base import BASE_DIR

env = environ.Env()
environ.Env.read_env(BASE_DIR / ".env")

SECRET_KEY = env("SECRET_KEY", default="dev-insecure-key-cambiar")
DEBUG = True
ALLOWED_HOSTS = ["*"]

DATABASES = {
    "default": env.db("DATABASE_URL", default="sqlite:///db.sqlite3")
}

CORS_ALLOW_ALL_ORIGINS = True
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# ── IA / Chatbot — se carga aquí DESPUÉS de read_env ─────────────────────────
GEMINI_API_KEY = env("GEMINI_API_KEY", default="")
