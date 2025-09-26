# forum/forms.py
from django import forms
from .models import Category,Topic, Reply

class TopicForm(forms.ModelForm):
    class Meta:
        model = Topic
        fields = ['title', 'category', 'content']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Korte, duidelijke titel'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 8,
                'placeholder': 'Omschrijf je onderwerp…'
            }),
        }

class ReplyForm(forms.ModelForm):
    class Meta:
        model = Reply
        fields = ['content', 'image']  # Include image if your form should allow image uploads
        widgets = {
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }
    content = forms.CharField(
        max_length=1000,  # Maximum length of content
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        label='Bericht'
    )
class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'image']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Bijv. Verwarming',
            }),
            'image': forms.ClearableFileInput(attrs={
                'class': 'form-control',   # Bootstrap 5 uses .form-control for file inputs
                'accept': 'image/*',       # <— this is what you tried to add in the template
            }),
        }