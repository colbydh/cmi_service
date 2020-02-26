from django.contrib.postgres.search import SearchQuery, SearchVector
from django.shortcuts import render
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status, viewsets
from rest_framework.views import APIView
from rest_framework.response import Response

from CMI_Service.settings import MAX_RECORDS_TO_RETURN

from socialmediapost.models import SocialMediaPost
from socialmediapost.serializers import SocialMediaPostHyperLinkListSerializer, \
    SocialMediaPostFullRepostedUserInfoFullSerializer, SocialMediaPostFullRepostedUserInfoHyperlinkedSerializer, \
    SocialMediaPostFullNoRepostedUserInfoSerializer


class SocialMediaPostViewSet(viewsets.ViewSet):
    """
    Handles the view set for social media posts.
    """

    @swagger_auto_schema(operation_description="Retrieve a list of social media posts.",
                         manual_parameters=[
                             openapi.Parameter('data-type', openapi.IN_QUERY,
                                               description='Sets type of return for the objects. "post" '
                                                           'returns full post object minus reposted_by. "url" '
                                                           'returns just the url to the post. "full" '
                                                           'returns full data for post and reposted_by. '
                                                           '"reposted_urls" returns full post object and urls '
                                                           'for reposted_by.',
                                               type=openapi.TYPE_STRING, default='post',
                                               enum=['post', 'url', 'full', 'resposted_urls']),
                             openapi.Parameter('search', openapi.IN_QUERY,
                                               description='Searches for a post that contains the specified string.',
                                               type=openapi.TYPE_STRING, default=''),
                             openapi.Parameter('author-id', openapi.IN_QUERY,
                                               description='Limits the posts returned to that of the author-id.',
                                               type=openapi.TYPE_INTEGER, default=''),
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
        author_id = int(request.GET['author-id']) if 'author-id' in request.GET.keys() else None

        if author_id:
            if search:
                search_query = SearchQuery(search)
                search_vector = SearchVector('author', 'hashtag_posts', 'keywords', 'user_mentions', 'reposted_by',
                                             'text',
                                             'sentiment', 'service')

                posts = SocialMediaPost.objects.annotate(
                    search=search_vector
                ).filter(
                    search=search_query,
                    author_id__exact=author_id
                ).order_by('-created_at')
            else:
                posts = SocialMediaPost.objects.filter(author_id__exact=author_id).order_by('-created_at')
        else:
            if search:
                search_query = SearchQuery(search)
                search_vector = SearchVector('author', 'hashtag_posts', 'keywords', 'user_mentions', 'reposted_by',
                                             'text',
                                             'sentiment', 'service')

                posts = SocialMediaPost.objects.annotate(
                    search=search_vector
                ).filter(
                    search=search_query,
                ).order_by('-created_at')
            else:
                posts = SocialMediaPost.objects.all().order_by('-created_at')

        total_counts = posts.count()
        posts = posts[offset:offset + limit]

        many = True

        # Based on the data_type serialize the users for return
        if data_type == 'post':
            serializer = SocialMediaPostFullNoRepostedUserInfoSerializer(posts, context={'request': request}, many=many)
        elif data_type == 'full':
            serializer = SocialMediaPostFullRepostedUserInfoFullSerializer(posts, context={'request': request},
                                                                           many=many)
        elif data_type == 'reposted_urls':
            serializer = SocialMediaPostFullRepostedUserInfoHyperlinkedSerializer(posts, context={'request': request},
                                                                                  many=many)
        else:  # 'urls'
            serializer = SocialMediaPostHyperLinkListSerializer(posts, context={'request': request}, many=many)

        next_offset = offset + limit

        if total_counts <= next_offset:
            next_offset = -1
        elif posts.count == 0:
            next_offset = -1

        # Create return dict
        return_dict = dict(
            records=posts.count(),
            next_offset=next_offset,
            data=serializer.data
        )

        return Response(return_dict)

    def create(self, request):
        Response({})

    @swagger_auto_schema(operation_description="Retrieve a specific of social media post.",
                         manual_parameters=[
                             openapi.Parameter('data-type', openapi.IN_QUERY,
                                               description='Sets type of return for the objects. "post" '
                                                           'returns full post object minus reposted_by. "url" '
                                                           'returns just the url to the post. "full" '
                                                           'returns full data for post and reposted_by. '
                                                           '"reposted_urls" returns full post object and urls '
                                                           'for reposted_by.',
                                               type=openapi.TYPE_STRING, default='post',
                                               enum=['post', 'url', 'full', 'friend_urls']),
                         ])
    def retrieve(self, request, pk=None):
        data_type = request.GET['data-type'] if 'data-type' in request.GET.keys() else None

        # Grab the user
        try:
            post = SocialMediaPost.objects.get(pk=pk)
        except SocialMediaPost.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        if data_type == 'url':
            serializer = SocialMediaPostHyperLinkListSerializer(post, context={'request': request})
        elif data_type == 'full':
            serializer = SocialMediaPostFullRepostedUserInfoFullSerializer(post, context={'request': request})
        elif data_type == 'friend_urls':
            serializer = SocialMediaPostFullRepostedUserInfoHyperlinkedSerializer(post, context={'request': request})
        else:
            serializer = SocialMediaPostFullNoRepostedUserInfoSerializer(post, context={'request': request})

        # Create return dict
        return_dict = dict(
            records=1,
            data=serializer.data
        )

        return Response(return_dict)

    def update(self, request, pk=None):
        Response({})

    def partial_update(self, request, pk=None):
        Response({})

    def destroy(self, request, pk=None):
        Response({})
