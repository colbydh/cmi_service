from rest_framework import serializers

from socialmediapost.models import SocialMediaPost, Hashtag
from socialmediauser.serializers import SocialMediaUserFullNoFriendsSerializer


# Hashtag serializer
from webarticles.serializers import UrlSerializer


class HashtagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Hashtag
        exclude = ['posts', 'id']


class SocialMediaPostHyperLinkListSerializer(serializers.HyperlinkedModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='socialmedia-post-detail')

    class Meta:
        model = SocialMediaPost
        fields = ['url']


# Serializes post with no reposted by info 'post'
class SocialMediaPostFullNoRepostedUserInfoSerializer(serializers.ModelSerializer):
    user_mentions = serializers.HyperlinkedRelatedField(
        many=True,
        read_only=True,
        view_name='socialmedia-user-detail'
    )
    hashtags = HashtagSerializer(many=True, source='hashtag_posts')
    urls = UrlSerializer(many=True, source='url_posts')

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        ret['repost_count'] = instance.get_repost_count()
        return ret

    class Meta:
        model = SocialMediaPost
        exclude = ['reposted_by']


# Serialized full post info with hyperlinks for the reposted_by 'repost_urls
class SocialMediaPostFullRepostedUserInfoHyperlinkedSerializer(serializers.ModelSerializer):
    reposted_by = serializers.HyperlinkedRelatedField(
        many=True,
        read_only=True,
        view_name='socialmedia-user-detail'
    )
    user_mentions = serializers.HyperlinkedRelatedField(
        many=True,
        read_only=True,
        view_name='socialmedia-user-detail'
    )
    hashtags = HashtagSerializer(many=True, source='hashtag_posts')
    urls = UrlSerializer(many=True, source='url_posts')

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        ret['repost_count'] = instance.get_repost_count()

        return ret

    class Meta:
        model = SocialMediaPost
        fields = '__all__'


# Serializes full post info with full reposted_by user info 'full'
class SocialMediaPostFullRepostedUserInfoFullSerializer(serializers.ModelSerializer):
    reposted_by = SocialMediaUserFullNoFriendsSerializer(many=True)
    user_mentions = SocialMediaUserFullNoFriendsSerializer(many=True)
    hashtags = HashtagSerializer(many=True, source='hashtag_posts')
    urls = UrlSerializer(many=True, source='url_posts')

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        ret['repost_count'] = instance.get_repost_count()

        return ret

    class Meta:
        model = SocialMediaPost
        fields = '__all__'

