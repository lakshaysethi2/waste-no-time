#!/bin/sh
python manage.py migrate
python manage.py run_bot &
gunicorn waste_no_time.wsgi:application --bind 0.0.0.0:8000 --workers 3
