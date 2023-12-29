from django import forms
from . import models

class CreateArticle(forms.ModelForm):
    class Meta: 
        model = models.NewsArticle
        fields = ['title','url','slug','date_published','thumb']
        