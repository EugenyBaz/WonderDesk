FROM python:3.12-slim-bullseye

WORKDIR /app

# Устанавливаем необходимые зависимости и очищаем кэш
RUN apt-get update && \
    apt-get install -y build-essential libpq-dev wget gnupg ca-certificates && \
    rm -rf /var/lib/apt/lists/*

COPY pyproject.toml poetry.lock ./

# Установка Poetry
RUN wget -O- https://install.python-poetry.org | PYTHONNOUSERSITE=1 python -

ENV PATH="/root/.local/bin:$PATH"

# Настройка виртуального окружения и установка зависимостей
RUN poetry config virtualenvs.create false && poetry install --no-root

COPY . .

EXPOSE 8000

CMD ["sh", "-c", "python manage.py collectstatic --noinput && gunicorn config.wsgi:application --bind 0.0.0.0:8000"]