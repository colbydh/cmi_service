from rest_framework import serializers

from socialmediapost.models import Hashtag
from webarticles.models import Url, Site, Article


class SiteHyperlinkSerializer(serializers.HyperlinkedModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='news-site-detail')

    class Meta:
        model = Site
        fields = ['url']


class SiteFullSerializer(serializers.ModelSerializer):
    class Meta:
        model = Site
        fields = '__all__'


class UrlSerializer(serializers.ModelSerializer):
    class Meta:
        model = Url
        fields = ['expanded']


class ArticleFullSerializer(serializers.ModelSerializer):
    class Meta:
        model = Article
        fields = '__all__'


class ArticleHyerlinkedSerializer(serializers.HyperlinkedModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='news-article-detail')

    class Meta:
        model = Article
        fields = ['url']
