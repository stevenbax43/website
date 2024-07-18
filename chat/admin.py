from django.contrib import admin
from .models import Conversation, SavedConversation
# Register your models here to be visable in the django/admin section

admin.site.register(Conversation)
admin.site.register(SavedConversation)