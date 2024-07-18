from django.db import models
from django.contrib.auth.models import User

class SavedConversation(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    title = models.CharField(max_length=255, default='Conversation')

    def __str__(self):
        return f"{self.title} by {self.author} at {self.created_at}"

class Conversation(models.Model):
    author_id = models.ForeignKey(User, default=None, on_delete=models.CASCADE, null=True)
    user_input = models.TextField()
    bot_response = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    saved_conversation = models.ForeignKey(SavedConversation, related_name='conversations', on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return f"{self.author_id}: {self.user_input}"
