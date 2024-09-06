# accounts/forms.py
from django import forms
from django.contrib.auth.models import User

class CustomUserChangeForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name')
        widgets = {
            'username': forms.TextInput(attrs={'readonly': 'readonly'}),
        }
        labels = {
            'username': 'Gebruikersnaam (niet te wijzigen)',      # Verbose name for username
            'email': 'Email-adres',     # Verbose name for email
            'first_name': 'Voornaam',   # Verbose name for first name
            'last_name': 'Achternaam',     # Verbose name for last name
        }