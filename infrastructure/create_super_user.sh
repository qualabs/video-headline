#!/bin/sh
username="$1"
email="$2"
password="$3"
organization_id= 1 

echo "
from django.contrib.auth import get_user_model
User = get_user_model()
try:
    User.objects.create_superuser(username='$username', email='$email', password='$password',organization_id='$organization_id')
    print('Superuser was created successfully: $username email: $email')
except Exception as e:
    print('Error when creating superuser:', str(e))
" | python manage.py shell