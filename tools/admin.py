from django.contrib import admin
from .models import adress

#this is the way we tell Django to register something on the admin site. 
admin.site.register(adress)