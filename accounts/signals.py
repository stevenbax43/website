from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver
from user_agents import parse

from .models import LoginActivity


@receiver(user_logged_in)
def log_user_login(sender, request, user, **kwargs):

    ip = request.META.get(
        "HTTP_X_FORWARDED_FOR",
        request.META.get("REMOTE_ADDR")
    )

    ua_string = request.META.get("HTTP_USER_AGENT", "")

    ua = parse(ua_string)

    browser = ua.browser.family
    device = ua.device.family
    os = ua.os.family

    LoginActivity.objects.create(
        user=user,
        ip_address=ip,
        user_agent=ua_string,
        browser=browser,
        device=device,
        os=os,
        success=True
    )