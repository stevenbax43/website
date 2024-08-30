# forum/models.py
from django.db import models
from django.contrib.auth.models import User

class Category(models.Model):
    name = models.CharField(max_length=200,  verbose_name='Naam')
    image = models.ImageField(upload_to='category_images/', blank=True, null=True,  verbose_name='Afbeelding')

    def __str__(self):
        return self.name

class Topic(models.Model):
    title = models.CharField(max_length=200, verbose_name='Titel')
    content = models.TextField(default='', verbose_name='Bericht')
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE,  null=True, blank=True, default=1, verbose_name='Categorie') 
    
    def __str__(self):
        return self.title

class Reply(models.Model):
    topic = models.ForeignKey(Topic, related_name='replies', null=True, blank=True, on_delete=models.CASCADE)
    content = models.TextField(verbose_name='Bericht')
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='replies_images/', blank=True, null=True, verbose_name='Afbeelding')
    parent_reply = models.ForeignKey('self', null=True, blank=True, related_name='child_replies', on_delete=models.CASCADE)

    def __str__(self):
        return f'In {self.topic} Reply on {self.parent_reply}'
 