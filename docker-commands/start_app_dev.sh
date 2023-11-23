#!/bin/bash

echo "Migrating and collecting statics"
python manage.py migrate --noinput # Apply database migrations

echo "Executing create_super_user.sh script"

# Set superuser credentials
username="${SUPERUSER_USERNAME}"
email="${SUPERUSER_EMAIL}"
password="${SUPERUSER_PASSWORD}"


echo "Creating superuser"

echo "
from django.contrib.auth import get_user_model
User = get_user_model()
try:
    User.objects.create_superuser('$username', '$email', '$password')
    print('Superuser was created successfully')
except Exception as e:
    print('Error when creating superuser:', str(e))
" | python manage.py shell


echo "Run the Django development server"
if [ "$1" == "plus" ]; then
  python manage.py runserver_plus 0:80
else
  python manage.py runserver 0:80
fi

