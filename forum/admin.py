from django.contrib import admin
from .models import Topic, Reply
# Register your models here to be visable in the django/admin section

admin.site.register(Topic)
admin.site.register(Reply)