from django.utils.deprecation import MiddlewareMixin


class SNSMiddleware(MiddlewareMixin):
    '''
    AWS SNS sends a JSON but with Content-Type text/plain.
    We need application/json for DRF Parser.
    '''

    def process_request(self, request):
        if request.META.get('HTTP_X_AMZ_SNS_MESSAGE_TYPE'):
            request.META['CONTENT_TYPE'] = 'application/json'
