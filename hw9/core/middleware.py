from django.core.exceptions import PermissionDenied
from django.http import Http404
from core.views import handler403, handler404


class BaseMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        return self.get_response(request)

    def process_exception(self, request, exception):
        raise NotImplementedError('process_exception not implemented')


class PermissionDeniedMiddleware(BaseMiddleware):
    def process_exception(self, request, exception):
        if isinstance(exception, PermissionDenied):
            return handler403(request, exception)


class PageNotFoundMiddleware(BaseMiddleware):
    def process_exception(self, request, exception):
        if isinstance(exception, Http404):
            return handler404(request, exception)
