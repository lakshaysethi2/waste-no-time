#!/bin/bash

# Run migrations
echo "Running migrations..."
python manage.py migrate --noinput

# Start Django web server in the background
echo "Starting Django server..."
gunicorn waste_no_time.wsgi:application --bind 0.0.0.0:8000 &

# Start the Telegram bot in the foreground
echo "Starting Telegram bot..."
python manage.py run_bot
