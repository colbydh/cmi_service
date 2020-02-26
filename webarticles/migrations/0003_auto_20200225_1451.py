# Generated by Django 3.0.3 on 2020-02-25 20:51

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('webarticles', '0002_auto_20200225_1434'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='url',
            name='date_published',
        ),
        migrations.AddField(
            model_name='url',
            name='expanded',
            field=models.CharField(max_length=2083, null=True),
        ),
        migrations.AlterField(
            model_name='url',
            name='article',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='webarticles.Article'),
        ),
    ]
