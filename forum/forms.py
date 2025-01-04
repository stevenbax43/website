from django import forms
from .models import Category,Topic, Reply


class TopicForm(forms.ModelForm):
    class Meta:
        model = Topic
        fields = ['title', 'category','content']

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
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }