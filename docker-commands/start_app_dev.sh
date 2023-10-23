#!/bin/bash

echo "Migrating and collecting statics"
python manage.py migrate --noinput # Apply database migrations

echo "Run the Django development server"
if [ "$1" == "plus" ]; then
  python manage.py runserver_plus 0:80
else
  python manage.py runserver 0:80
fi
