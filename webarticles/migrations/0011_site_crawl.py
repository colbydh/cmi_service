# Generated by Django 3.0.3 on 2020-02-26 14:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('webarticles', '0010_auto_20200226_0750'),
    ]

    operations = [
        migrations.AddField(
            model_name='site',
            name='crawl',
            field=models.BooleanField(default=True),
        ),
    ]
