from django.conf import settings
from django.db import models


class LoginActivity(models.Model):

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )

    timestamp = models.DateTimeField(auto_now_add=True)

    ip_address = models.GenericIPAddressField(null=True, blank=True)

    user_agent = models.TextField(blank=True)

    browser = models.CharField(max_length=100, blank=True)
    device = models.CharField(max_length=100, blank=True)
    os = models.CharField(max_length=100, blank=True)

    country = models.CharField(max_length=100, blank=True)

    success = models.BooleanField(default=True)

    username_attempted = models.CharField(max_length=150, blank=True)

    def __str__(self):
        return f"{self.user} - {self.timestamp}"