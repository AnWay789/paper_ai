#!/bin/sh
set -e

mkdir -p /app/data
# Подтягиваем зависимости при обновлении pyproject.toml / poetry.lock (volume mount в dev)
poetry install --no-ansi --no-root
poetry run python manage.py migrate --noinput

exec "$@"
