from django.db import models
from django.contrib.auth.models import User

class Conversation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, default=None)
    title = models.CharField(max_length=100,default='A')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} door: {self.user}"

class SingleUserBot(models.Model):
    user = models.ForeignKey(User, default=None, on_delete=models.CASCADE)
    user_input = models.TextField()
    bot_response = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    parent = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='bot_entries', null=True, blank=True)

    def __str__(self):
        return f"{self.user}: {self.user_input}"

