from django.contrib import admin
from .models import Conversation, SingleUserBot
# Register your models here to be visable in the django/admin section
class ConversationAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'created_at')  # Adjust fields to display
    list_filter = ('user',)  # Add filter by user

admin.site.register(Conversation,ConversationAdmin)
admin.site.register(SingleUserBot)