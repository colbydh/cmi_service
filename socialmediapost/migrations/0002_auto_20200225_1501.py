# Generated by Django 3.0.3 on 2020-02-25 21:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('socialmediapost', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='hashtag',
            name='posts',
            field=models.ManyToManyField(blank=True, related_name='hashtag_posts', to='socialmediapost.SocialMediaPost'),
        ),
    ]