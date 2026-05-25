FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_CREATE=false \
    PYTHONPATH=/app/src

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/* \
    && pip install --no-cache-dir poetry

COPY pyproject.toml poetry.lock README.md ./
COPY manage.py ./
COPY src ./src
RUN poetry install --no-ansi --no-root

COPY docker/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

RUN mkdir -p /app/data

EXPOSE 8000

ENTRYPOINT ["/entrypoint.sh"]
CMD ["poetry", "run", "python", "manage.py", "runserver", "0.0.0.0:8000"]
