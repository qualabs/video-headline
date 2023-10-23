from rest_framework.authentication import SessionAuthentication
from rest_framework import authentication
from rest_framework import exceptions

from hub_auth.models import APIKey


class CsrfExemptSessionAuthentication(SessionAuthentication):
    def enforce_csrf(self, request):
        return  # To not perform the csrf check previously happening


class APIKeyAuthentication(authentication.BaseAuthentication):
    def authenticate(self, request):
        api_key = request.META.get('HTTP_AUTHORIZATION', '')
        if not api_key:
            return None

        try:
            api = APIKey.objects.get(api_key=api_key)
        except APIKey.DoesNotExist:
            raise exceptions.AuthenticationFailed('Invalid API Key.')

        return api.account, None
