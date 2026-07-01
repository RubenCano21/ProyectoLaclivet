FROM python:3.13-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev gcc && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV DJANGO_SETTINGS_MODULE=config.settings.prod

RUN DJANGO_SETTINGS_MODULE=config.settings.prod \
    SECRET_KEY=build-time-dummy-key \
    DATABASE_URL=sqlite:///db.sqlite3 \
    ALLOWED_HOSTS=localhost \
    CORS_ALLOWED_ORIGINS=http://localhost \
    CSRF_TRUSTED_ORIGINS=http://localhost \
    GS_BUCKET_NAME=dummy \
    GCP_PROJECT_ID=dummy \
    EMAIL_HOST=dummy \
    EMAIL_HOST_USER=dummy \
    EMAIL_HOST_PASSWORD=dummy \
    python manage.py collectstatic --noinput

# Seguridad: no correr el proceso de la aplicación como root dentro del
# contenedor (defensa en profundidad si el contenedor llega a ser comprometido).
RUN addgroup --system app && adduser --system --ingroup app --home /app app \
    && chown -R app:app /app
USER app

EXPOSE 8080

CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8080", "--workers", "3"]