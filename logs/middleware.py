import json
from .models import APIRequestLog
from django.utils.deprecation import MiddlewareMixin
from django.utils import timezone

class APIRequestLoggingMiddleware(MiddlewareMixin):
    def process_request(self, request):
        if request.path.startswith('/api/'):
            request.request_data = self.extract_request_data(request)

    def process_response(self, request, response):
        if request.path.startswith('/api/'):
            # Log the API request and response
            api_url = request.path
            request_data = self.extract_request_data(request)
            response_data = response.content
            datetime = timezone.now()
            ip_address = request.META.get('REMOTE_ADDR')
            response_status = response.status_code
            request_method = request.method
            request_user = request.user

            # Save the log entry
            log_entry = APIRequestLog(
                api_url=api_url,
                request_data=request_data,
                response_data=response_data,
                datetime=datetime,
                ip_address=ip_address,
                response_status=response_status,
                request_method=request_method,
                request_user=request_user,
            )
            log_entry.save()

        return response

    def extract_request_data(self, request):
        # Extract request data based on content type
        if request.method == 'GET':
            return json.dumps(dict(request.GET))
        elif request.method == 'POST':
            # if 'application/json' in request.content_type:
            #     return request.body
            # elif 'multipart/form-data' in request.content_type:
            #     return json.dumps(dict(request.POST))
            # else:
            #     return request.body
            
            if 'multipart/form-data' in request.content_type:
                return json.dumps(dict(request.POST))
            else:
                return request.body
        else:
            return request.body
