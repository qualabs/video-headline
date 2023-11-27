#!/bin/sh
username="$1"
email="$2"
password="$3"

echo "
from django.contrib.auth import get_user_model
User = get_user_model()
try:
    User.objects.create_superuser('$username', '$email', '$password')
    print('Superuser was created successfully: $username email: $email')
except Exception as e:
    print('Error when creating superuser:', str(e))
" | python manage.py shell