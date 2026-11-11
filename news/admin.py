from django.contrib import admin
from .models import NewsArticle
class NewsArticleAdmin(admin.ModelAdmin):
    list_display = ('title', 'slug','author_id', 'date_published_text')  # Adjust fields to display
    list_filter = ('slug',)  # Add filter by user

admin.site.register(NewsArticle,NewsArticleAdmin)
