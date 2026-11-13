from django.contrib import admin
from .models import Category, Topic, Reply

class ReplyAdmin(admin.ModelAdmin):
    list_display = ('topic', 'created_at', 'created_by', 'parent_reply')  # Customize fields to display
    list_filter = ('created_by',)  # Add filters by user and topic
class TopicAdmin(admin.ModelAdmin):
    list_display = ('title',  'created_by','created_at', 'category')  # Customize fields to display
    list_filter = ('created_by',)  # Add filters by user and topic

admin.site.register(Category)
admin.site.register(Topic, TopicAdmin)
admin.site.register(Reply,ReplyAdmin)
