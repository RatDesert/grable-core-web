#!/usr/bin/env bash
cd src
python manage.py makemigrations --noinput
python manage.py migrate --noinput
python manage.py collectstatic --noinput
python manage.py compilemessages

gunicorn wsgi -b 0.0.0.0:8000 --timeout 60 --reload
