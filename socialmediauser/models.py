from django.contrib.postgres.fields import ArrayField, JSONField
from django.db import models


class SocialMediaCountry(models.Model):
    """
    Country
    Defines the attributes for Country
    """

    class Meta:
        db_table = 'socialmediacountry'

    name = models.TextField()
    identifier = models.CharField(max_length=4)
    actors = ArrayField(models.BigIntegerField(), null=True)
    sentiment_for_actor = JSONField(null=True)


class SocialMediaUser(models.Model):
    """
    Social Media User
    Defines the attributes for the social media user
    """

    class Meta:
        db_table = 'socialmediauser'

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
    country = models.ForeignKey(SocialMediaCountry, on_delete=models.DO_NOTHING, null=True)

    def get_follower_count(self):
        return self.twitter_followers.count()

    def get_follows_count(self):
        return self.twitter_follows.count()

