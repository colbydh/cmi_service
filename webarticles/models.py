from datetime import datetime

from django.contrib.postgres.fields import ArrayField, JSONField
from django.db import models

# The maximum length of URL allowed.
from socialmediapost.models import SocialMediaPost

MAX_URL_LEN = 2083


class Site(models.Model):
    """Table `site` to record site information.

    Relations
    ---------
    site <-- ONE TO MANY --> article
    site <-- ONE TO MANY --> urls
    """
    name = models.CharField(null=False, max_length=255, unique=True)
    domain = models.CharField(null=False, max_length=255, unique=True)
    base_url = models.CharField(null=False, max_length=511, unique=True)
    crawl = models.BooleanField(default=True)


class Article(models.Model):
    """Table `article` to record article from news site.

    Relations
    ---------
    article <-- ONE TO MANY --> url
    article <-- MANY TO ONE --> site
    """

    class Meta:
        db_table = 'article'

    expanded_url = models.CharField(null=False, max_length=MAX_URL_LEN, unique=True)
    authors = ArrayField(models.CharField(max_length=255), null=True)
    keywords = ArrayField(models.CharField(max_length=255), null=True)
    lang = models.CharField(null=True, max_length=4)
    title = models.CharField(null=False, max_length=255)
    meta = JSONField(null=True)
    text = models.TextField(null=False)
    date_published = models.DateTimeField(null=True)


class Url(models.Model):
    """The url table store URLs collected either from social networks or
    websites.

    Relations
    ---------
    url <-- MANY TO ONE  --> article
    url <-- MANY TO MANY --> post

    Columns
    -------
    raw : string(MAX_URL_LEN)
        The original url from site or tweet.
    expended : string(MAX_URL_LEN)
        The unshorten version of url that uses shorten service.
    scraped: bool
        True if the url has been scrapped for data
    """

    class Meta:
        db_table = 'url'

    raw = models.CharField(null=True, max_length=MAX_URL_LEN)
    expanded = models.CharField(null=True, max_length=MAX_URL_LEN, unique=True)
    canonical = models.CharField(null=True, max_length=MAX_URL_LEN, unique=True)
    scraped = models.BooleanField(default=False)

    # relationships
    article = models.ForeignKey(Article, on_delete=models.CASCADE, null=True)
    posts = models.ManyToManyField(SocialMediaPost, blank=True, related_name='url_posts')
    site = models.ForeignKey(Site, on_delete=models.CASCADE, null=True)







