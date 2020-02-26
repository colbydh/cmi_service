# Serialized full user info with hyperlinks for the followers and who they follow 'friend_urls
from rest_framework import serializers

from socialmediauser.models import SocialMediaUser


class SocialMediaUserFullFriendsHyperLinkedSerializer(serializers.ModelSerializer):
    twitter_followers = serializers.HyperlinkedRelatedField(
        many=True,
        read_only=True,
        view_name='socialmedia-user-detail'
    )
    twitter_follows = serializers.HyperlinkedRelatedField(
        many=True,
        read_only=True,
        view_name='socialmedia-user-detail'
    )

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        ret['twitter_follower_count'] = instance.get_follower_count()
        ret['twitter_follows_count'] = instance.get_follows_count()

        return ret

    class Meta:
        model = SocialMediaUser
        fields = '__all__'


# Serializes full user info with no follower or follows data 'user'
class SocialMediaUserFullNoFriendsSerializer(serializers.ModelSerializer):

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        ret['twitter_follower_count'] = instance.get_follower_count()
        ret['twitter_follows_count'] = instance.get_follows_count()

        return ret

    class Meta:
        model = SocialMediaUser
        exclude = ['twitter_followers', 'twitter_follows']


# Serializes full user info with full follower and follows user info 'full'
class SocialMediaUserFullFriendsSerializer(serializers.ModelSerializer):
    twitter_followers = SocialMediaUserFullNoFriendsSerializer(many=True)
    twitter_follows = SocialMediaUserFullNoFriendsSerializer(many=True)

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        ret['twitter_follower_count'] = instance.get_follower_count()
        ret['twitter_follows_count'] = instance.get_follows_count()

        return ret

    class Meta:
        model = SocialMediaUser
        fields = '__all__'


# Serializes urls for users 'urls'
class SocialMediaUserHyperLinkListSerializer(serializers.HyperlinkedModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='socialmedia-user-detail')

    class Meta:
        model = SocialMediaUser
        fields = ['url']