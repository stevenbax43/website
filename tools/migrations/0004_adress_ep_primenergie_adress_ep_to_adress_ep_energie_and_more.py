# Generated by Django 4.2.9 on 2024-07-12 13:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tools', '0003_alter_adress_addition_alter_adress_elektra_terug'),
    ]

    operations = [
        migrations.AddField(
            model_name='adress',
            name='EP_PrimEnergie',
            field=models.TextField(default='', max_length=5),
        ),
        migrations.AddField(
            model_name='adress',
            name='EP_TO',
            field=models.TextField(default='', max_length=5),
        ),
        migrations.AddField(
            model_name='adress',
            name='EP_energie',
            field=models.TextField(default='', max_length=5),
        ),
        migrations.AddField(
            model_name='adress',
            name='EP_gebouwklasse',
            field=models.TextField(default='', max_length=5),
        ),
        migrations.AddField(
            model_name='adress',
            name='EP_surface',
            field=models.TextField(default='', max_length=5),
        ),
        migrations.AddField(
            model_name='adress',
            name='EP_warmte',
            field=models.TextField(default='', max_length=5),
        ),
        migrations.AlterField(
            model_name='adress',
            name='EP_label',
            field=models.TextField(default='', max_length=5),
        ),
    ]
