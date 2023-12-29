from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class NewsArticle(models.Model):
    title = models.CharField(max_length=255, default='')
    url = models.CharField(max_length=400, unique=True)
    slug = models.SlugField()    
    date_created = models.DateTimeField(null=True)
    date_published = models.CharField(max_length=255, default='')
    author_id = models.ForeignKey(User, default=None, on_delete=models.SET_NULL, null=True) 
    thumb = models.ImageField(upload_to='news_thumbs/', default='default.png', blank=True)

    def save(self, *args, **kwargs):
        if not self.date_created:
            self.date_created = timezone.now()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

    def snippet(self):
        return self.url[:30] + "..."