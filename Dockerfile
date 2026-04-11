FROM python:3.12-slim

RUN apt-get update && apt-get install -y \
    gettext \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements/ requirements/
RUN pip install --no-cache-dir -r requirements/base.txt

COPY . .

RUN useradd -m appuser && chown -R appuser:appuser /app
USER appuser

ENTRYPOINT ["scripts/entrypoint.sh"]
CMD ["daphne", "-b", "0.0.0.0", "-p", "8000", "settings.asgi:application"]
