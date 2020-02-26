from django.contrib.postgres.search import SearchQuery, SearchVector
from django.test import TestCase, RequestFactory
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from webarticles.models import Site
from webarticles.serializers import SiteHyperlinkSerializer, SiteFullSerializer

client = APIClient()


class NewsSiteTest(TestCase):
    """ Test Module for News Sites """

    def setUp(self):
        self.site_one = Site.objects.create(name='Site One', domain='Domain One', base_url='http://www.siteone.com')

    def test_news_site_post(self):

        # Post data
        site = {'name': 'Test Site', 'domain': 'test.com'}

        # Post it
        response = client.post(reverse('news-site-list'), site)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, {'error': 'name, domain, and base_url must be provided.'})

        site['base_url'] = 'http://www.test.com'
        response = client.post(reverse('news-site-list'), site)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Site.objects.filter(name='Test Site').exists())

        response = client.post(reverse('news-site-list'), site)
        self.assertEqual(response.status_code, status.HTTP_303_SEE_OTHER)

    def test_get_all_sites_hyperlinked(self):
        limit = 100
        offset = 0
        # From db direct
        sites = Site.objects.all()[offset:offset + limit]

        # from api
        response = client.get(reverse('news-site-list'))

        context = {'request': RequestFactory().get('/')}

        serializer = SiteHyperlinkSerializer(sites, many=True, context=context)
        test_response = dict(
            records=sites.count(),
            next_offset=-1,
            data=serializer.data
        )
        self.assertEqual(response.data, test_response)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_all_sites_full(self):
        limit = 100
        offset = 0
        # From db direct
        sites = Site.objects.all()[offset:offset + limit]

        # from api
        response = client.get(reverse('news-site-list'), data={'data-type': 'full'})

        context = {'request': RequestFactory().get('/')}

        serializer = SiteFullSerializer(sites, many=True, context=context)
        test_response = dict(
            records=sites.count(),
            next_offset=-1,
            data=serializer.data
        )
        self.assertEqual(response.data, test_response)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_site_full(self):
        # From db direct
        posts = Site.objects.get(pk=self.site_one.pk)

        # from api
        response = client.get(reverse('news-site-detail', kwargs={'pk': self.site_one.pk}),
                              data={'data-type': 'full'})

        context = {'request': RequestFactory().get('/')}

        serializer = SiteFullSerializer(posts, context=context)
        test_response = dict(
            records=1,
            data=serializer.data
        )
        self.assertEqual(response.data, test_response)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_search_sites(self):
        search_query = SearchQuery('domain one')
        search_vector = SearchVector('name', 'domain', 'base_url')

        posts = Site.objects.annotate(
            search=search_vector
        ).filter(
            search=search_query
        )

        # from api
        response = client.get(reverse('news-site-list'), data={'search': 'domain one', 'data-type': 'full'})

        # Serializer
        context = {'request': RequestFactory().get('/')}
        serializer = SiteFullSerializer(posts, many=True, context=context)

        test_response = dict(
            records=posts.count(),
            next_offset=-1,
            data=serializer.data
        )
        self.assertEqual(response.data, test_response)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_patch_sites(self):
        # Post data
        site = {'domain': 'testtwo.com'}

        # Post it
        response = client.put(reverse('news-site-detail', kwargs={'pk': self.site_one.pk}), data=site, format='json',)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, {'error': 'name must be provided.'})

        site = {'name': self.site_one.name, 'domain': 'testtwo.com'}
        response = client.put(reverse('news-site-detail', kwargs={'pk': self.site_one.pk}), data=site, format='json',)
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)
        tmp_obj = Site.objects.get(name=self.site_one.name)
        self.assertEqual(tmp_obj.domain, 'testtwo.com')

        site = {'name': self.site_one.name, 'base_url': 'http://www.testtwo.com'}
        response = client.patch(reverse('news-site-detail', kwargs={'pk': self.site_one.pk}), data=site, format='json',)
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)
        tmp_obj = Site.objects.get(name=self.site_one.name)
        self.assertEqual(tmp_obj.base_url, 'http://www.testtwo.com')

    def test_delete(self):
        # Post it
        response = client.delete(reverse('news-site-detail', kwargs={'pk': self.site_one.pk}))
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)
        self.assertFalse(Site.objects.filter(name=self.site_one.name).exists())


class NewsArticleTest(TestCase):
    pass