from datetime import datetime

from django.contrib.postgres.search import SearchQuery, SearchVector
from django.test import TestCase, Client
from django.urls import reverse
from rest_framework import status
from django.test.client import RequestFactory

# initialize the APIClient app
from socialmediapost.models import SocialMediaPost, Hashtag
from socialmediapost.serializers import SocialMediaPostHyperLinkListSerializer, \
    SocialMediaPostFullNoRepostedUserInfoSerializer, SocialMediaPostFullRepostedUserInfoHyperlinkedSerializer, \
    SocialMediaPostFullRepostedUserInfoFullSerializer
from socialmediauser.models import SocialMediaUser

client = Client()


class SocialMediaPostTest(TestCase):
    """ Test Module for Social Media Post """

    def setUp(self):
        self.author = SocialMediaUser.objects.create(name='Test One', is_influencer=True,
                                                     twitter_screen_name='TwitterOne',
                                                     twitter_user_id=1, facebook_screen_name='FacebookOne',
                                                     location='Cloud City', lat=10.10, lon=10.10,
                                                     twitter_posts_count=10, network_graph={})
        self.retweeter = SocialMediaUser.objects.create(name='Test Two', is_influencer=False,
                                                        twitter_screen_name='TwitterTwo',
                                                        twitter_user_id=2, facebook_screen_name='FacebookTwo',
                                                        location='Cloud City', lat=10.10, lon=10.10,
                                                        twitter_posts_count=10, network_graph={})
        self.post_one = SocialMediaPost.objects.create(author=self.author, created_at=datetime.now(),
                                                       post_id=1, lang='en', reply_count=0,
                                                       text="'I'm a new post", service='Twitter')
        self.post_two = SocialMediaPost.objects.create(author=self.retweeter, created_at=datetime.now(),
                                                       post_id=1, lang='en', reply_count=0,
                                                       text="'I'm a new post", service='Twitter')
        self.hashtag = Hashtag.objects.create(text='Hashtags')

    def test_post_attributes(self):
        self.post_one.reposted_by.add(self.retweeter)
        self.hashtag.posts.add(self.post_one)
        self.assertEqual(self.post_one.author.name, 'Test One')
        self.assertEqual(self.post_one.reposted_by.count(), 1)

    def test_get_all_posts_hyperlinked(self):
        limit = 100
        offset = 0
        # From db direct
        posts = SocialMediaPost.objects.all().order_by('-created_at')[offset:offset + limit]

        # from api
        response = client.get(reverse('socialmedia-post-list'))

        context = {'request': RequestFactory().get('/')}

        serializer = SocialMediaPostHyperLinkListSerializer(posts, many=True, context=context)
        test_response = dict(
            records=posts.count(),
            next_offset=-1,
            data=serializer.data
        )
        self.assertEqual(response.data, test_response)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_all_posts_no_reposted_by_full(self):
        limit = 100
        offset = 0
        # From db direct
        posts = SocialMediaPost.objects.all().order_by('-created_at')[offset:offset + limit]

        # from api
        response = client.get(reverse('socialmedia-post-list'), data={'data-type': 'post'})

        context = {'request': RequestFactory().get('/')}

        serializer = SocialMediaPostFullNoRepostedUserInfoSerializer(posts, many=True, context=context)
        test_response = dict(
            records=posts.count(),
            next_offset=-1,
            data=serializer.data
        )
        self.assertEqual(response.data, test_response)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_all_posts_reposted_by_hyperlinked(self):
        limit = 100
        offset = 0
        # From db direct
        posts = SocialMediaPost.objects.all().order_by('-created_at')[offset:offset + limit]

        # from api
        response = client.get(reverse('socialmedia-post-list'), data={'data-type': 'reposted_urls'})

        context = {'request': RequestFactory().get('/')}

        serializer = SocialMediaPostFullRepostedUserInfoHyperlinkedSerializer(posts, many=True, context=context)
        test_response = dict(
            records=posts.count(),
            next_offset=-1,
            data=serializer.data
        )
        self.assertEqual(response.data, test_response)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_all_posts_reposted_by_full(self):
        limit = 100
        offset = 0
        # From db direct
        posts = SocialMediaPost.objects.all().order_by('-created_at')[offset:offset + limit]

        # from api
        response = client.get(reverse('socialmedia-post-list'), data={'data-type': 'full'})

        context = {'request': RequestFactory().get('/')}

        serializer = SocialMediaPostFullRepostedUserInfoFullSerializer(posts, many=True, context=context)
        test_response = dict(
            records=posts.count(),
            next_offset=-1,
            data=serializer.data
        )
        self.assertEqual(response.data, test_response)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_post_no_reposted_by_full(self):
        # From db direct
        posts = SocialMediaPost.objects.get(pk=self.post_one.pk)

        # from api
        response = client.get(reverse('socialmedia-post-detail', kwargs={'pk': self.post_one.pk}), data={'data-type': 'post'})

        context = {'request': RequestFactory().get('/')}

        serializer = SocialMediaPostFullNoRepostedUserInfoSerializer(posts, context=context)
        test_response = dict(
            records=1,
            data=serializer.data
        )
        self.assertEqual(response.data, test_response)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_posts_reposted_by_hyperlinked(self):
        # From db direct
        posts = SocialMediaPost.objects.get(pk=self.post_one.pk)

        # from api
        response = client.get(reverse('socialmedia-post-detail', kwargs={'pk': self.post_one.pk}), data={'data-type': 'post'})

        context = {'request': RequestFactory().get('/')}

        serializer = SocialMediaPostFullNoRepostedUserInfoSerializer(posts, context=context)
        test_response = dict(
            records=1,
            data=serializer.data
        )
        self.assertEqual(response.data, test_response)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_posts_reposted_by_full(self):
        # From db direct
        posts = SocialMediaPost.objects.get(pk=self.post_one.pk)

        # from api
        response = client.get(reverse('socialmedia-post-detail', kwargs={'pk': self.post_one.pk}), data={'data-type': 'full'})

        context = {'request': RequestFactory().get('/')}

        serializer = SocialMediaPostFullRepostedUserInfoFullSerializer(posts, context=context)
        test_response = dict(
            records=1,
            data=serializer.data
        )
        self.assertEqual(response.data, test_response)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_posts_search(self):
        search_query = SearchQuery('hashtags')
        search_vector = SearchVector('author', 'hashtag_posts', 'keywords', 'user_mentions', 'reposted_by', 'text',
                                     'sentiment', 'service')

        posts = SocialMediaPost.objects.annotate(
            search=search_vector
        ).filter(
            search=search_query
        )

        # from api
        response = client.get(reverse('socialmedia-post-list'), data={'search': 'hashtags'})

        # Serializer
        context = {'request': RequestFactory().get('/')}
        serializer = SocialMediaPostHyperLinkListSerializer(posts, many=True, context=context)

        test_response = dict(
            records=posts.count(),
            next_offset=-1,
            data=serializer.data
        )
        self.assertEqual(response.data, test_response)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_posts_by_author_id(self):
        limit = 100
        offset = 0
        # From db direct
        posts = SocialMediaPost.objects.filter(author_id__exact=self.author.pk).order_by('-created_at')[offset:offset + limit]

        # from api
        response = client.get(reverse('socialmedia-post-list'), data={'data-type': 'post', 'author-id': self.author.pk})

        context = {'request': RequestFactory().get('/')}

        serializer = SocialMediaPostFullNoRepostedUserInfoSerializer(posts, many=True, context=context)
        test_response = dict(
            records=posts.count(),
            next_offset=-1,
            data=serializer.data
        )
        self.assertEqual(response.data, test_response)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


