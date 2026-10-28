#!/bin/sh
set -e

python manage.py migrate --noinput
python manage.py collectstatic --noinput

# The logger class keeps query strings (search terms) out of the access log
exec gunicorn config.wsgi:application \
  --bind 0.0.0.0:8000 \
  --workers 3 \
  --access-logfile - \
  --logger-class config.gunicorn_logger.AccessLogger \
  --error-logfile -
