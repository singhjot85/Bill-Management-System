import logging
import time

from django.conf import settings
from django.utils.deprecation import MiddlewareMixin

logger = logging.getLogger(__name__)


class RequestLoggingMiddleware(MiddlewareMixin):
    """Middleware to log request/response details"""

    def process_request(self, request):
        request.start_time = time.time()

        # Log request details
        if settings.DEBUG:
            logger.debug(
                f"Request: {request.method} {request.path}",
                extra={
                    "method": request.method,
                    "path": request.path,
                    "user": str(request.user) if request.user.is_authenticated else "Anonymous",
                    "ip": self.get_client_ip(request),
                },
            )

    def process_response(self, request, response):
        if hasattr(request, "start_time"):
            duration = time.time() - request.start_time

            # Log response details
            log_data = {
                "method": request.method,
                "path": request.path,
                "status": response.status_code,
                "duration": f"{duration:.4f}s",
                "ip": self.get_client_ip(request),
                "user_agent": request.META.get("HTTP_USER_AGENT", ""),
            }

            # Log based on status code
            if response.status_code >= 500:
                logger.error(f"Server Error: {response.status_code}", extra=log_data)
            elif response.status_code >= 400:
                logger.warning(f"Client Error: {response.status_code}", extra=log_data)
            else:
                logger.info(f"Response: {response.status_code}", extra=log_data)

        return response

    def get_client_ip(self, request):
        """Get client IP from request"""
        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded_for:
            ip = x_forwarded_for.split(",")[0]
        else:
            ip = request.META.get("REMOTE_ADDR")
        return ip
