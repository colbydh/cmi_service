# Generated by Django 3.0.3 on 2020-02-24 20:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('common', '0005_auto_20200224_1011'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='socialmediapost',
            name='user_mentions',
        ),
        migrations.AddField(
            model_name='socialmediapost',
            name='user_mentions',
            field=models.ManyToManyField(blank=True, related_name='user_mentions', to='common.SocialMediaUser'),
        ),
    ]