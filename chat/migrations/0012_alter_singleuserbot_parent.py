# Generated by Django 4.2.9 on 2024-08-30 09:11

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('chat', '0011_alter_singleuserbot_parent'),
    ]

    operations = [
        migrations.AlterField(
            model_name='singleuserbot',
            name='parent',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='bot_entries', to='chat.conversation'),
        ),
    ]
