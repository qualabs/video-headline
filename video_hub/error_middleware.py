from django.http import HttpResponseServerError
from django.conf import settings
import botocore.exceptions



class ErrorMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if settings.DEBUG:
            print(f"Request: {request.path}")
        try:
            response = self.get_response(request)
        except Exception as ex:
            print(f"Error Middleware: {ex}")
            response = HttpResponseServerError(ex)
            
        return response
