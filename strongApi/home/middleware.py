from django.utils.decorators import decorator_from_middleware
from django.middleware.csrf import CsrfViewMiddleware

class CsrfExemptMiddleware(CsrfViewMiddleware):
    def process_view(self, request, callback, callback_args, callback_kwargs):
        # Check if the view is an API view based on your URL pattern or other conditions
        # For example, you can check if the URL starts with '/api/' or contains 'api/' in the path
        if "api/" in request.path:
            return None
        return super().process_view(request, callback, callback_args, callback_kwargs)

# Create a decorator from the middleware class
csrf_exempt_api = decorator_from_middleware(CsrfExemptMiddleware)


# important !
# this middleware is created by chat gtp