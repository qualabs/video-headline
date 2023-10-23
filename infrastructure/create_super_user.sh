#!/bin/sh
username="admin"
email="admin@admin.com"
password="12345678"
echo "
from django.contrib.auth import get_user_model
User = get_user_model()
try:
    User.objects.create_superuser('$username', '$email', '$password')
    print('Superuser was created successfully')
except Exception as e:
    print('Error when creating superuser:', str(e))
" | python manage.py shell