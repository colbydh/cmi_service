# Generated by Django 3.0.3 on 2020-02-25 19:45

import django.contrib.postgres.fields
import django.contrib.postgres.fields.jsonb
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='SocialMediaCountry',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.TextField()),
                ('identifier', models.CharField(max_length=4)),
                ('actors', django.contrib.postgres.fields.ArrayField(base_field=models.BigIntegerField(), null=True, size=None)),
                ('sentiment_for_actor', django.contrib.postgres.fields.jsonb.JSONField(null=True)),
            ],
            options={
                'db_table': 'socialmediacountry',
            },
        ),
        migrations.CreateModel(
            name='SocialMediaUser',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.TextField(null=True)),
                ('is_influencer', models.BooleanField(null=True)),
                ('twitter_screen_name', models.TextField(null=True)),
                ('twitter_user_id', models.BigIntegerField(null=True)),
                ('facebook_screen_name', models.TextField(null=True)),
                ('location', models.TextField(null=True)),
                ('lat', models.FloatField(null=True)),
                ('lon', models.FloatField(null=True)),
                ('twitter_posts_count', models.IntegerField(null=True)),
                ('network_graph', django.contrib.postgres.fields.jsonb.JSONField(null=True)),
                ('country', models.ForeignKey(null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='socialmediauser.SocialMediaCountry')),
                ('twitter_followers', models.ManyToManyField(blank=True, related_name='followers_twitter', to='socialmediauser.SocialMediaUser')),
                ('twitter_follows', models.ManyToManyField(blank=True, related_name='follows_twitter', to='socialmediauser.SocialMediaUser')),
            ],
            options={
                'db_table': 'socialmediauser',
            },
        ),
    ]
