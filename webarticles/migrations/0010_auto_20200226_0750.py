# Generated by Django 3.0.3 on 2020-02-26 13:50

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('webarticles', '0009_auto_20200226_0739'),
    ]

    operations = [
        migrations.RenameField(
            model_name='article',
            old_name='canonical',
            new_name='expanded_url',
        ),
        migrations.RemoveField(
            model_name='url',
            name='canonical',
        ),
    ]
