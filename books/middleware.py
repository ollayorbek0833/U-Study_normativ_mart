from django.conf import settings
from django.utils import timezone


class RequestLoggerMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        now = timezone.now().strftime("%Y-%m-%d %H:%M")
        user = request.user.username if request.user.is_authenticated else "AnonymousUser"
        ip = request.META.get('REMOTE_ADDR', '')
        path = request.path
        log_entry = f"[{now}]\nUser: {user}\nIP: {ip}\nPath: {path}\n\n"
        log_file = settings.BASE_DIR / 'requests.log'
        with open(log_file, 'a') as f:
            f.write(log_entry)
        return response
