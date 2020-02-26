from django.contrib.postgres.search import SearchQuery, SearchVector
from django.shortcuts import render
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status, viewsets
from rest_framework.views import APIView
from rest_framework.response import Response

from CMI_Service.settings import MAX_RECORDS_TO_RETURN
from webarticles.models import Site, Article
from webarticles.serializers import SiteHyperlinkSerializer, SiteFullSerializer, ArticleFullSerializer


# View set for the News Site Model
class NewsSiteViewSet(viewsets.ViewSet):
    """
    Handles the view set for news sites.
    """

    @swagger_auto_schema(operation_description="Retrieve a list of social media posts.",
                         manual_parameters=[
                             openapi.Parameter('data-type', openapi.IN_QUERY,
                                               description='Sets the return type for the site data. "url" returns a '
                                                           'list of urls to the site objects. "full" returns the full '
                                                           'site objects.',
                                               type=openapi.TYPE_STRING, default='full',
                                               enum=['url', 'full']),
                             openapi.Parameter('search', openapi.IN_QUERY,
                                               description='Searches for a site that contains the specified string.',
                                               type=openapi.TYPE_STRING, default=''),
                             openapi.Parameter('limit', openapi.IN_QUERY, description='Limits the return count.',
                                               type=openapi.TYPE_INTEGER, default=''),
                             openapi.Parameter('offset', openapi.IN_QUERY,
                                               description='Offset to start at for the query.',
                                               type=openapi.TYPE_INTEGER, default=''),
                         ])
    def list(self, request):
        data_type = request.GET['data-type'] if 'data-type' in request.GET.keys() else None
        limit = int(request.GET['limit']) if 'limit' in request.GET.keys() else MAX_RECORDS_TO_RETURN
        offset = int(request.GET['offset']) if 'offset' in request.GET.keys() else 0
        search = request.GET['search'] if 'search' in request.GET.keys() else None

        if search:
            search_query = SearchQuery(search)
            search_vector = SearchVector('name', 'domain', 'base_url')
            sites = Site.objects.annotate(search=search_vector).filter(search=search_query)
        else:
            sites = Site.objects.all()

        total_counts = sites.count()
        sites = sites[offset:offset + limit]

        many = True

        # Based on the data_type serialize the users for return
        if data_type == 'full':
            serializer = SiteFullSerializer(sites, context={'request': request}, many=many)
        else:  # 'urls'
            serializer = SiteHyperlinkSerializer(sites, context={'request': request}, many=many)

        next_offset = offset + limit

        if total_counts <= next_offset:
            next_offset = -1
        elif sites.count == 0:
            next_offset = -1

        # Create return dict
        return_dict = dict(
            records=sites.count(),
            next_offset=next_offset,
            data=serializer.data
        )

        return Response(return_dict)

    @swagger_auto_schema(operation_description="Create news site.",
                         request_body=openapi.Schema(
                             type=openapi.TYPE_OBJECT,
                             required=['name', 'domain', 'base_url'],
                             properties={
                                 'name': openapi.Schema(type=openapi.TYPE_STRING),
                                 'domain': openapi.Schema(type=openapi.TYPE_STRING),
                                 'base_url': openapi.Schema(type=openapi.TYPE_STRING)
                             },
                         ),
                         security=[])
    def create(self, request):
        # Get the post data
        data = request.data
        name = data['name'] if 'name' in data.keys() else None
        domain = data['domain'] if 'domain' in data.keys() else None
        base_url = data['base_url'] if 'base_url' in data.keys() else None

        # If the fields are none then error
        if name is None or domain is None or base_url is None:
            return Response(status=status.HTTP_400_BAD_REQUEST, data={'error': 'name, domain, and base_url must be provided.'})

        # Check if object exists
        try:
            site = Site.objects.get(name=data['name'])
            if site:
                serializer = SiteHyperlinkSerializer(site, context={'request': request})
                return Response(status=status.HTTP_303_SEE_OTHER, data={'existing_item': serializer.data})
            else:
                site = Site.objects.create(name=data['name'], domain=data['domain'], base_url=data['base_url'])
                if site:
                    return Response(status=status.HTTP_201_CREATED)
        except:
            site = Site.objects.create(name=data['name'], domain=data['domain'], base_url=data['base_url'])
            if site:
                return Response(status=status.HTTP_201_CREATED)

    @swagger_auto_schema(operation_description="Retrieve a specific of site.",
                         manual_parameters=[
                             openapi.Parameter('data-type', openapi.IN_QUERY,
                                               description='Sets the return type for the site data. "url" returns a '
                                                           'list of urls to the site objects. "full" returns the full '
                                                           'site objects.',
                                               type=openapi.TYPE_STRING, default='full',
                                               enum=['url', 'full']),
                         ])
    def retrieve(self, request, pk=None):
        data_type = request.GET['data-type'] if 'data-type' in request.GET.keys() else None

        # Grab the user
        try:
            post = Site.objects.get(pk=pk)
        except Site.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        if data_type == 'url':
            serializer = SiteHyperlinkSerializer(post, context={'request': request})
        else:
            serializer = SiteFullSerializer(post, context={'request': request})

        # Create return dict
        return_dict = dict(
            records=1,
            data=serializer.data
        )

        return Response(return_dict)

    @swagger_auto_schema(operation_description="Updates the news site.",
                         request_body=openapi.Schema(
                             type=openapi.TYPE_OBJECT,
                             required=['name'],
                             properties={
                                 'name': openapi.Schema(type=openapi.TYPE_STRING),
                                 'domain': openapi.Schema(type=openapi.TYPE_STRING),
                                 'base_url': openapi.Schema(type=openapi.TYPE_STRING)
                             },
                         ),
                         security=[])
    def update(self, request, pk=None):
        # Get the post data
        data = request.data

        return self.update_helper(pk, data)

    @swagger_auto_schema(operation_description="Updates the news site.",
                         request_body=openapi.Schema(
                             type=openapi.TYPE_OBJECT,
                             required=['name'],
                             properties={
                                 'name': openapi.Schema(type=openapi.TYPE_STRING),
                                 'domain': openapi.Schema(type=openapi.TYPE_STRING),
                                 'base_url': openapi.Schema(type=openapi.TYPE_STRING)
                             },
                         ),
                         security=[])
    def partial_update(self, request, pk=None):
        # Get the post data
        data = request.data

        return self.update_helper(pk, data)

    @swagger_auto_schema(operation_description="Deletes the site.",
                         security=[])
    def destroy(self, request, pk=None):
        try:
            site = Site.objects.get(pk=pk)
            site.delete()
            return Response(status=status.HTTP_202_ACCEPTED)
        except:
            return Response(status=status.HTTP_404_NOT_FOUND)

    # Helper function to update site data
    def update_helper(self, pk=None, data=None):
        name = data['name'] if 'name' in data.keys() else None
        domain = data['domain'] if 'domain' in data.keys() else None
        base_url = data['base_url'] if 'base_url' in data.keys() else None

        # If the fields are none then error
        if name is None:
            return Response(status=status.HTTP_400_BAD_REQUEST,
                            data={'error': 'name must be provided.'})

        # Check if object exists
        try:
            site = Site.objects.get(name=data['name'])
            if site:
                if domain:
                    site.domain = domain
                if base_url:
                    site.base_url = base_url
                site.save()
                return Response(status=status.HTTP_202_ACCEPTED)
            else:
                return Response(status=status.HTTP_404_NOT_FOUND)
        except:
            return Response(status=status.HTTP_404_NOT_FOUND)


class ArticleViewSet(viewsets.ViewSet):
    """
    Handles the view set for news articles.
    """

    def list(self, request):
        articles = Article.objects.all()
        serializer = ArticleFullSerializer(articles, many=True)
        return Response(serializer.data)


    def retrieve(self, request, pk=None):
        Response({})

