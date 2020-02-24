#from djongo import models
from django.db import models
from django.contrib.postgres.fields import ArrayField, JSONField


class SocialMediaUser(models.Model):
    """
    Social Media User
    Defines the attributes for the social media user
    """
    name = models.TextField(null=True)
    is_influencer = models.BooleanField(null=True)
    twitter_screen_name = models.TextField(null=True)
    twitter_user_id = models.BigIntegerField(null=True)
    facebook_screen_name = models.TextField(null=True)
    location = models.TextField(null=True)
    lat = models.FloatField(null=True)
    lon = models.FloatField(null=True)
    twitter_follows = models.ManyToManyField('self', blank=True, symmetrical=False, related_name='follows_twitter')
    twitter_followers = models.ManyToManyField('self', blank=True, symmetrical=False, related_name='followers_twitter')
    twitter_posts_count = models.IntegerField(null=True)
    network_graph = JSONField(null=True)
    country = models.ForeignKey('SocialMediaCountry', on_delete=models.DO_NOTHING, null=True)

    def get_follower_count(self):
        return self.twitter_followers.count()

    def get_follows_count(self):
        return self.twitter_follows.count()


class SocialMediaPost(models.Model):
    """
    Social Media Post
    Defines the attributes for the social media post
    """
    author = models.ForeignKey('SocialMediaUser', on_delete=models.CASCADE, null=True)
    created_at = models.DateTimeField(blank=True)
    hashtags = ArrayField(models.TextField(blank=True), null=True)
    keywords = ArrayField(models.TextField(blank=True), null=True)
    user_mentions = models.ManyToManyField('SocialMediaUser', blank=True, symmetrical=False, related_name='user_mentions')
    post_id = models.BigIntegerField(blank=True, null=True)
    in_reply_to_user_id = models.BigIntegerField(blank=True, null=True)
    in_reply_to_post_id = models.BigIntegerField(blank=True, null=True)
    lang = models.CharField(max_length=20, null=True)
    reply_count = models.IntegerField(blank=True, null=True)
    reposted_by = models.ManyToManyField('SocialMediaUser', blank=True, symmetrical=False, related_name='reposted_by')
    text = models.TextField(blank=True)
    sentiment = models.CharField(max_length=20, null=True)
    service = models.CharField(max_length=20)

    def get_repost_count(self):
        return self.reposted_by.count()


class SocialMediaCountry(models.Model):
    """
    Country
    Defines the attributes for Country
    """
    name = models.TextField()
    identifier = models.CharField(max_length=4)
    actors = ArrayField(models.BigIntegerField(), null=True)
    sentiment_for_actor = JSONField(null=True)
