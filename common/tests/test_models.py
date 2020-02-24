from datetime import datetime

from django.contrib.postgres.search import SearchQuery, SearchVector
from django.test import TestCase, Client
from django.urls import reverse
from rest_framework import status
from django.test.client import RequestFactory

from ..models import SocialMediaUser, SocialMediaPost
from ..serializers import SocialMediaUserFullNoFriendsSerializer, SocialMediaUserFullFriendsHyperLinkedSerializer, \
    SocialMediaUserHyperLinkListSerializer, SocialMediaUserFullFriendsSerializer, SocialMediaPostHyperLinkListSerializer, \
    SocialMediaPostFullNoRepostedUserInfoSerializer, SocialMediaPostFullRepostedUserInfoHyperlinkedSerializer, \
    SocialMediaPostFullRepostedUserInfoFullSerializer

# initialize the APIClient app
client = Client()


class SocialMediaUserTest(TestCase):
    """ Test Module for Social Media User """

    def setUp(self):
        self.one = SocialMediaUser.objects.create(name='Test One', is_influencer=True, twitter_screen_name='TwitterOne',
                                                  twitter_user_id=1, facebook_screen_name='FacebookOne',
                                                  location='Cloud City',
                                                  lat=10.10, lon=10.10, twitter_posts_count=10, network_graph={})
        self.two = SocialMediaUser.objects.create(name='Test Two', is_influencer=False,
                                                  twitter_screen_name='TwitterTwo',
                                                  twitter_user_id=2, facebook_screen_name='FacebookTwo',
                                                  location='Cloud City',
                                                  lat=10.10, lon=10.10, twitter_posts_count=10, network_graph={})
        self.three = SocialMediaUser.objects.create(name='Test Three', is_influencer=False,
                                                    twitter_screen_name='TwitterThree',
                                                    twitter_user_id=3, facebook_screen_name='FacebookThree',
                                                    location='Tattooine',
                                                    lat=10.10, lon=10.10, twitter_posts_count=10, network_graph={})

    def test_social_media_user_attributes(self):
        user_test_one = SocialMediaUser.objects.get(name='Test One')
        user_test_two = SocialMediaUser.objects.get(twitter_screen_name='TwitterTwo')
        user_test_three = SocialMediaUser.objects.get(facebook_screen_name='FacebookThree')

        user_test_one.twitter_followers.add(user_test_two)
        user_test_one.twitter_followers.add(user_test_three)

        user_test_two.twitter_follows.add(user_test_one)
        user_test_three.twitter_follows.add(user_test_one)

        self.assertEqual(user_test_one.name, 'Test One')
        self.assertEqual(user_test_two.name, 'Test Two')
        self.assertEqual(user_test_three.name, 'Test Three')
        self.assertEqual(user_test_one.twitter_followers.count(), 2)
        self.assertEqual(user_test_two.twitter_follows.count(), 1)
        self.assertEqual(user_test_three.twitter_followers.count(), 0)

    def test_get_all_users_hyperlinked(self):
        limit = 100
        offset = 0
        # From db direct
        users = SocialMediaUser.objects.all()[offset:offset + limit]

        # from api
        response = client.get(reverse('socialmediauser-list'))

        context = {'request': RequestFactory().get('/')}

        serializer = SocialMediaUserHyperLinkListSerializer(users, many=True, context=context)
        test_response = dict(
            records=users.count(),
            next_offset=-1,
            data=serializer.data
        )
        self.assertEqual(response.data, test_response)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_all_users_followers_hyperlinked(self):
        limit = 100
        offset = 0
        # From db direct
        users = SocialMediaUser.objects.all()[offset:offset + limit]

        # from api
        response = client.get(reverse('socialmediauser-list'), data={'data-type': 'friend_urls'})

        context = {'request': RequestFactory().get('/')}

        serializer = SocialMediaUserFullFriendsHyperLinkedSerializer(users, many=True, context=context)
        test_response = dict(
            records=users.count(),
            next_offset=-1,
            data=serializer.data
        )
        self.assertEqual(response.data, test_response)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_all_users_followers_full(self):
        limit = 100
        offset = 0
        # From db direct
        users = SocialMediaUser.objects.all()[offset:offset + limit]

        # from api
        response = client.get(reverse('socialmediauser-list'), data={'data-type': 'full'})

        context = {'request': RequestFactory().get('/')}

        serializer = SocialMediaUserFullFriendsSerializer(users, many=True, context=context)
        test_response = dict(
            records=users.count(),
            next_offset=-1,
            data=serializer.data
        )
        self.assertEqual(response.data, test_response)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_all_users_no_followers_full(self):
        limit = 100
        offset = 0
        # From db direct
        users = SocialMediaUser.objects.all()[offset:offset + limit]

        # from api
        response = client.get(reverse('socialmediauser-list'), data={'data-type': 'user'})

        context = {'request': RequestFactory().get('/')}

        serializer = SocialMediaUserFullNoFriendsSerializer(users, many=True, context=context)
        test_response = dict(
            records=users.count(),
            next_offset=-1,
            data=serializer.data
        )
        self.assertEqual(response.data, test_response)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_user_followers_hyperlinked(self):
        # From db direct
        user = SocialMediaUser.objects.get(pk=self.one.pk)

        # from api
        response = client.get(reverse('socialmediauser-detail', kwargs={'pk': self.one.pk}),
                              data={'data-type': 'friend_urls'})

        context = {'request': RequestFactory().get('/')}

        serializer = SocialMediaUserFullFriendsHyperLinkedSerializer(user, context=context)
        test_response = dict(
            records=1,
            data=serializer.data
        )
        self.assertEqual(response.data, test_response)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_user_followers_followers_full(self):
        # From db direct
        user = SocialMediaUser.objects.get(pk=self.two.pk)

        # from api
        response = client.get(reverse('socialmediauser-detail', kwargs={'pk': self.two.pk}),
                              data={'data-type': 'full'})

        context = {'request': RequestFactory().get('/')}

        serializer = SocialMediaUserFullFriendsSerializer(user, context=context)
        test_response = dict(
            records=1,
            data=serializer.data
        )
        self.assertEqual(response.data, test_response)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_user_followers_no_followers_full(self):
        # From db direct
        user = SocialMediaUser.objects.get(pk=self.three.pk)

        # from api
        response = client.get(reverse('socialmediauser-detail', kwargs={'pk': self.three.pk}),
                              data={'data-type': 'user'})

        context = {'request': RequestFactory().get('/')}

        serializer = SocialMediaUserFullNoFriendsSerializer(user, context=context)
        test_response = dict(
            records=1,
            data=serializer.data
        )
        self.assertEqual(response.data, test_response)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_user_invalid(self):
        # from api
        response = client.get(reverse('socialmediauser-detail', kwargs={'pk': 99}),
                              data={'data-type': 'user'})
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_limits_and_offsets(self):
        limit = 2
        offset = 0
        # From db direct
        users = SocialMediaUser.objects.all()[offset:offset + limit]

        # from api
        response = client.get(reverse('socialmediauser-list'), data={'offset': offset, 'limit': limit})

        context = {'request': RequestFactory().get('/')}

        serializer = SocialMediaUserHyperLinkListSerializer(users, many=True, context=context)
        test_response = dict(
            records=users.count(),
            next_offset=2,
            data=serializer.data
        )
        self.assertEqual(response.data, test_response)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_search(self):
        search_query = SearchQuery('Cloud City')
        search_vector = SearchVector('name', 'twitter_screen_name', 'facebook_screen_name', 'location')

        users = SocialMediaUser.objects.annotate(
            search=search_vector
        ).filter(
            search=search_query
        )

        # from api
        response = client.get(reverse('socialmediauser-list'), data={'search': 'Cloud City'})

        # Serializer
        context = {'request': RequestFactory().get('/')}
        serializer = SocialMediaUserHyperLinkListSerializer(users, many=True, context=context)

        test_response = dict(
            records=users.count(),
            next_offset=-1,
            data=serializer.data
        )
        self.assertEqual(response.data, test_response)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


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
                                                       hashtags=['hashtags'], post_id=1, lang='en', reply_count=0,
                                                       text="'I'm a new post", service='Twitter')
        self.post_two = SocialMediaPost.objects.create(author=self.retweeter, created_at=datetime.now(),
                                                       hashtags=['hashtags'], post_id=1, lang='en', reply_count=0,
                                                       text="'I'm a new post", service='Twitter')

    def test_post_attributes(self):
        self.post_one.reposted_by.add(self.retweeter)

        self.assertEqual(self.post_one.author.name, 'Test One')
        self.assertEqual(self.post_one.reposted_by.count(), 1)

    def test_get_all_posts_hyperlinked(self):
        limit = 100
        offset = 0
        # From db direct
        posts = SocialMediaPost.objects.all().order_by('-created_at')[offset:offset + limit]

        # from api
        response = client.get(reverse('socialmediapost-list'))

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
        response = client.get(reverse('socialmediapost-list'), data={'data-type': 'post'})

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
        response = client.get(reverse('socialmediapost-list'), data={'data-type': 'reposted_urls'})

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
        response = client.get(reverse('socialmediapost-list'), data={'data-type': 'full'})

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
        response = client.get(reverse('socialmediapost-detail', kwargs={'pk': self.post_one.pk}), data={'data-type': 'post'})

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
        response = client.get(reverse('socialmediapost-detail', kwargs={'pk': self.post_one.pk}), data={'data-type': 'post'})

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
        response = client.get(reverse('socialmediapost-detail', kwargs={'pk': self.post_one.pk}), data={'data-type': 'full'})

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
        search_vector = SearchVector('author', 'hashtags', 'keywords', 'user_mentions', 'reposted_by', 'text',
                                     'sentiment', 'service')

        posts = SocialMediaPost.objects.annotate(
            search=search_vector
        ).filter(
            search=search_query
        )

        # from api
        response = client.get(reverse('socialmediapost-list'), data={'search': 'hashtags'})

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
        response = client.get(reverse('socialmediapost-list'), data={'data-type': 'post', 'author-id': self.author.pk})

        context = {'request': RequestFactory().get('/')}

        serializer = SocialMediaPostFullNoRepostedUserInfoSerializer(posts, many=True, context=context)
        test_response = dict(
            records=posts.count(),
            next_offset=-1,
            data=serializer.data
        )
        self.assertEqual(response.data, test_response)
        self.assertEqual(response.status_code, status.HTTP_200_OK)