# Generated by Django 4.2.9 on 2024-09-24 12:51

import ckeditor.fields
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('forum', '0004_topic_is_closed'),
    ]

    operations = [
        migrations.AlterField(
            model_name='topic',
            name='content',
            field=ckeditor.fields.RichTextField(default='', verbose_name='Bericht'),
        ),
    ]
