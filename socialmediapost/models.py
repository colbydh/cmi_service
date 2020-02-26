from django.contrib.postgres.fields import ArrayField, JSONField
from django.db import models

from socialmediauser.models import SocialMediaUser


class SocialMediaPost(models.Model):
    """
    Social Media Post
    Defines the attributes for the social media post
    """

    class Meta:
        db_table = 'socialmediapost'

    author = models.ForeignKey(SocialMediaUser, on_delete=models.CASCADE, null=True)
    created_at = models.DateTimeField(blank=True)
    keywords = ArrayField(models.TextField(blank=True), null=True)
    user_mentions = models.ManyToManyField(SocialMediaUser, blank=True, symmetrical=False,
                                           related_name='user_mentions')
    post_id = models.BigIntegerField(blank=True, null=True)
    in_reply_to_user_id = models.BigIntegerField(blank=True, null=True)
    in_reply_to_post_id = models.BigIntegerField(blank=True, null=True)
    lang = models.CharField(max_length=20, null=True)
    reply_count = models.IntegerField(blank=True, null=True)
    reposted_by = models.ManyToManyField(SocialMediaUser, blank=True, symmetrical=False, related_name='reposted_by')
    text = models.TextField(blank=True)
    sentiment = models.CharField(max_length=20, null=True)
    service = models.CharField(max_length=20)

    def get_repost_count(self):
        return self.reposted_by.count()


class Hashtag(models.Model):
    """Table `hashtag`, hashtag used in tweet or other social networks.

    Relations
    ---------
    hashtag <-- MANY TO MANY --> tweet
    """
    class Meta:
        db_table = 'hashtag'

    text = models.CharField(null=False, max_length=255, unique=True)
    # relationship attributes
    posts = models.ManyToManyField(SocialMediaPost, blank=True, related_name='hashtag_posts')



