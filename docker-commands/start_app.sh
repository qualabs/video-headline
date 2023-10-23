#!/bin/bash

echo "Migrating DB"
python manage.py migrate --noinput # Apply database migrations

echo "Starting nginx"
service nginx start

echo "Starting uWSGI"
uwsgi --ini /etc/uwsgi/uwsgi.ini
