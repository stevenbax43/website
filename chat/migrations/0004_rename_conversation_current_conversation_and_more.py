# Generated by Django 4.2.9 on 2024-08-19 12:45

from django.conf import settings
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('chat', '0003_savedconversation_title'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Conversation',
            new_name='Current_Conversation',
        ),
        migrations.RenameModel(
            old_name='SavedConversation',
            new_name='Saved_Conversations',
        ),
    ]
