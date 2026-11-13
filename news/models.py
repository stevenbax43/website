from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class NewsArticle(models.Model):
    title = models.CharField(max_length=255, default='')
    url = models.CharField(max_length=400, unique=True)
    slug = models.SlugField(default='')    
    date_created = models.DateTimeField(null=True)
    date_published_datetime = models.DateTimeField(null=True)
    date_published_text = models.CharField(max_length=255, default='')
    author_id = models.ForeignKey(User, default=None, on_delete=models.SET_NULL, null=True) 
    thumb = models.ImageField(upload_to='news_images/', default='default.png', blank=True)

    def save(self, *args, **kwargs):
        if not self.date_created:
            self.date_created = timezone.now()
        # Generate the slug before saving
        if not self.slug:
            self.slug = self.snippet()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

    def snippet(self):
    # Check if the URL length is greater than 27 characters
        if len(self.url) > 27:
            # Take the first 17 characters, then take the last 10 of these 17 characters
            first_part = self.url[:25]
            last_10_of_first_part = first_part[12:]  # Get the last 10 characters of the first 17 characters
            return last_10_of_first_part + "..."
        return self.url
