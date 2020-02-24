from rest_framework import serializers
from common.models import SocialMediaUser, SocialMediaPost, SocialMediaCountry


# ### SOCIAL MEDIA USERS SERIALIZERS ### #

# Serialized full user info with hyperlinks for the followers and who they follow 'friend_urls
class SocialMediaUserFullFriendsHyperLinkedSerializer(serializers.ModelSerializer):
    twitter_followers = serializers.HyperlinkedRelatedField(
        many=True,
        read_only=True,
        view_name='socialmediauser-detail'
    )
    twitter_follows = serializers.HyperlinkedRelatedField(
        many=True,
        read_only=True,
        view_name='socialmediauser-detail'
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
    class Meta:
        model = SocialMediaUser
        fields = ['url']


# ### SOCIAL MEDIA POSTS SERIALIZERS ### #

# Serializes urls for posts 'urls'
class SocialMediaPostHyperLinkListSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = SocialMediaPost
        fields = ['url']


# Serializes post with no reposted by info 'post'
class SocialMediaPostFullNoRepostedUserInfoSerializer(serializers.ModelSerializer):
    user_mentions = serializers.HyperlinkedRelatedField(
        many=True,
        read_only=True,
        view_name='socialmediauser-detail'
    )

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
        view_name='socialmediauser-detail'
    )
    user_mentions = serializers.HyperlinkedRelatedField(
        many=True,
        read_only=True,
        view_name='socialmediauser-detail'
    )

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

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        ret['repost_count'] = instance.get_repost_count()

        return ret

    class Meta:
        model = SocialMediaPost
        fields = '__all__'