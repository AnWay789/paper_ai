#!/bin/sh
set -e

mkdir -p /app/data
poetry run python manage.py migrate --noinput

exec "$@"
