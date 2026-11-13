from django.contrib import admin
from .models import LoginActivity
# Register your models here.



@admin.register(LoginActivity)
class LoginActivityAdmin(admin.ModelAdmin):

    list_display = (
        "user",
        "timestamp",
        "ip_address",
        "browser",
        "device",
        "country",
        "success",
    )

    list_filter = ("browser", "device", "country", "success")

    search_fields = ("user__username", "ip_address")