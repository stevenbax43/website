# Generated by Django 4.2.9 on 2024-07-13 19:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('chat', '0002_savedconversation_conversation_saved_conversation'),
    ]

    operations = [
        migrations.AddField(
            model_name='savedconversation',
            name='title',
            field=models.CharField(default='Conversation', max_length=255),
        ),
    ]
