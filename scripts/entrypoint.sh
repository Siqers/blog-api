#!/bin/sh

echo "Waiting for Redis..."
until redis-cli -h redis ping; do
  sleep 1
done

echo "Running migrations..."
python manage.py migrate

echo "Collecting static files..."
python manage.py collectstatic --noinput

echo "Compiling messages..."
python manage.py compilemessages

if [ "$BLOG_SEED_DB" = "true" ]; then
  echo "Seeding database..."
  python manage.py seed
fi

exec "$@"
