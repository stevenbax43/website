# Generated by Django 4.2.9 on 2024-08-19 12:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('news', '0002_rename_date_published_newsarticle_date_published_text_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='newsarticle',
            name='thumb',
            field=models.ImageField(blank=True, default='default.png', upload_to='news_images/'),
        ),
    ]
