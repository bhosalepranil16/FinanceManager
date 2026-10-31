# Built from the repo root (docker-compose.yml `context: .`).
# Runtime settings (port, workers, secrets) are injected by Compose from FinaceManager/.env.
FROM python:3.12-slim AS builder

ENV PIP_NO_CACHE_DIR=1 PIP_DISABLE_PIP_VERSION_CHECK=1
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY requirements.txt .
RUN pip install -r requirements.txt


FROM python:3.12-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/opt/venv/bin:$PATH"

COPY --from=builder /opt/venv /opt/venv

RUN useradd --create-home --uid 1000 app
WORKDIR /app

# Created and chowned before the volumes mount so the named volumes inherit app ownership.
RUN mkdir -p /app/staticfiles /app/media && chown -R app:app /app

COPY --chown=app:app . .

USER app

# Migrations and static collection run on every start, so `git pull` + rebuild is all an update needs.
CMD ["sh", "-c", "python manage.py migrate --noinput && python manage.py collectstatic --noinput && exec gunicorn FinaceManager.wsgi:application --bind 0.0.0.0:${APP_PORT} --workers ${WEB_CONCURRENCY} --access-logfile -"]
