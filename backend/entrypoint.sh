#!/bin/sh
set -e

python manage.py migrate --noinput
python manage.py collectstatic --noinput

# The logger class keeps query strings (search terms) out of the access log.
# WEB_CONCURRENCY: worker processes, about 2 per CPU core. A worker is restarted after
# about 1000 requests, so memory cannot creep up over weeks.
exec gunicorn config.wsgi:application \
  --bind 0.0.0.0:8000 \
  --workers "${WEB_CONCURRENCY:-3}" \
  --timeout "${GUNICORN_TIMEOUT:-30}" \
  --max-requests 1000 \
  --max-requests-jitter 100 \
  --access-logfile - \
  --logger-class config.gunicorn_logger.AccessLogger \
  --error-logfile -
