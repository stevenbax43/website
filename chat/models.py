from django.db import models
from django.contrib.auth.models import User

class Conversation(models.Model):
    author_id = models.ForeignKey(User, default=None, on_delete=models.CASCADE, null=True)
    user_input = models.TextField()
    bot_response = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    

    def __str__(self):
        return f"{self.author_id}: {self.user_input}"
       