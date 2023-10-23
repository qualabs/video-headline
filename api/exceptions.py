from rest_framework import status
from rest_framework.exceptions import APIException


class WrongPassword(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'The current password entered is not correct, please verify'
    default_code = 'wrong_password'

class SubscriptionError(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Could not subscribe to alert service'
    default_code = 'subscription_error'