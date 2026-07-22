#!/bin/bash
set -euo pipefail

python manage.py migrate --noinput

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput

# Start Django web server in the background
echo "Starting Django server..."
gunicorn waste_no_time.wsgi:application --bind 0.0.0.0:8000 &
web_pid=$!
python manage.py run_bot &
bot_pid=$!

cleanup() {
  kill "$web_pid" "$bot_pid" 2>/dev/null || true
  wait "$web_pid" "$bot_pid" 2>/dev/null || true
}
trap cleanup EXIT INT TERM

# A failure in either required process stops the container so Compose can restart it.
wait -n "$web_pid" "$bot_pid"
exit $?
