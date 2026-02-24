"""Middleware for audit context (user + IP) capture."""
from core.signals import set_request_context, clear_request_context


class AuditMiddleware:
    """Captures request user and IP for audit logging."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        user = request.user if hasattr(request, 'user') else None
        ip = self._get_client_ip(request)
        set_request_context(user, ip)
        response = self.get_response(request)
        clear_request_context()
        return response

    @staticmethod
    def _get_client_ip(request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0].strip()
        return request.META.get('REMOTE_ADDR')
