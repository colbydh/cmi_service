from django.contrib.postgres.search import SearchQuery, SearchVector
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework.permissions import AllowAny
from rest_framework.schemas import SchemaGenerator
from rest_framework_swagger import renderers

from common.models import SocialMediaUser, SocialMediaPost, SocialMediaCountry
from rest_framework import viewsets, permissions, status
from .serializers import SocialMediaUserHyperLinkListSerializer, SocialMediaUser, \
    SocialMediaUserFullFriendsHyperLinkedSerializer, SocialMediaUserFullNoFriendsSerializer, \
    SocialMediaUserFullFriendsSerializer, SocialMediaPostFullNoRepostedUserInfoSerializer, \
    SocialMediaPostFullRepostedUserInfoFullSerializer, SocialMediaPostFullRepostedUserInfoHyperlinkedSerializer, \
    SocialMediaPostHyperLinkListSerializer
from rest_framework.views import APIView
from rest_framework.response import Response

MAX_RECORDS_TO_RETURN = 100

# ### SOCIAL MEDIA USER API ### #


class SocialMediaUsers(APIView):
    """
    Returns a SocialMediaUser object for the provided id.
    """

    @swagger_auto_schema(manual_parameters=[
        openapi.Parameter('data-type', openapi.IN_QUERY, description='Sets type of return for the objects. "user" '
                                                                     'returns full user object minus friends. "url" '
                                                                     'returns just the url to the user. "full" '
                                                                     'returns full data for user and friends. '
                                                                     '"friend_urls" returns full user object and urls '
                                                                     'for friends.',
                          type=openapi.TYPE_STRING, default='user', enum=['user', 'url', 'full', 'friend_urls'])
    ])
    def get(self, request, pk=-1, format=None):
        data_type = request.GET['data-type'] if 'data-type' in request.GET.keys() else None

        # Grab the user
        try:
            user = SocialMediaUser.objects.get(pk=pk)
        except SocialMediaUser.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        if data_type == 'url':
            serializer = SocialMediaUserHyperLinkListSerializer(user, context={'request': request})
        elif data_type == 'full':
            serializer = SocialMediaUserFullFriendsSerializer(user, context={'request': request})
        elif data_type == 'friend_urls':
            serializer = SocialMediaUserFullFriendsHyperLinkedSerializer(user, context={'request': request})
        else:
            serializer = SocialMediaUserFullNoFriendsSerializer(user, context={'request': request})

        # Create return dict
        return_dict = dict(
            records=1,
            data=serializer.data
        )

        return Response(return_dict)

    def get_extra_actions(self):
        return []


class SocialMediaUsersList(APIView):
    """
    Returns a list SocialMediaUsers.
    """

    @swagger_auto_schema(manual_parameters=[
        openapi.Parameter('data-type', openapi.IN_QUERY, description='Sets type of return for the objects. "user" '
                                                                     'returns full user object minus friends. "url" '
                                                                     'returns just the url to the user. "full" '
                                                                     'returns full data for user and friends. '
                                                                     '"friend_urls" returns full user object and urls '
                                                                     'for friends.',
                          type=openapi.TYPE_STRING, default='user', enum=['user', 'url', 'full', 'friend_urls']),
        openapi.Parameter('influencers-only', openapi.IN_QUERY, description='If set to true will only retrieve '
                                                                            'influencers.',
                          type=openapi.TYPE_BOOLEAN, default=False),
        openapi.Parameter('has-coordinates', openapi.IN_QUERY, description='If set to true will only retrieve '
                                                                           'users with coordinates.',
                          type=openapi.TYPE_BOOLEAN, default=False),
        openapi.Parameter('search', openapi.IN_QUERY, description='Searches for a user that contains the string.',
                          type=openapi.TYPE_STRING, default=''),
        openapi.Parameter('limit', openapi.IN_QUERY, description='Limits the return count.',
                          type=openapi.TYPE_INTEGER, default=''),
        openapi.Parameter('offset', openapi.IN_QUERY, description='Offset to start at for the query.',
                          type=openapi.TYPE_INTEGER, default=''),
    ])
    def get(self, request, format=None):
        data_type = request.GET['data-type'] if 'data-type' in request.GET.keys() else None
        influencers_only = request.GET['influencers-only'] if 'influencers-only' in request.GET.keys() else None
        has_coordinates = request.GET['has-coordinates'] if 'has-coordinates' in request.GET.keys() else None
        limit = int(request.GET['limit']) if 'limit' in request.GET.keys() else MAX_RECORDS_TO_RETURN
        offset = int(request.GET['offset']) if 'offset' in request.GET.keys() else 0
        search = request.GET['search'] if 'search' in request.GET.keys() else None

        # Check to see if we will filter for influencers
        if influencers_only is None:
            influencers_only = None
        elif influencers_only.lower() == 'true':
            influencers_only = True
        else:
            influencers_only = False

        # Check to see if we will filter out the ones with no geo data
        if has_coordinates is None:
            allow_coordinates_null = True
        elif has_coordinates.lower() == 'true':
            allow_coordinates_null = False
        else:
            allow_coordinates_null = True

        if search:
            search_query = SearchQuery(search)
            search_vector = SearchVector('name', 'twitter_screen_name', 'facebook_screen_name', 'location')

            users = SocialMediaUser.objects.annotate(
                search=search_vector
            ).filter(
                search=search_query
            )[offset:offset + limit]
        else:
            users = SocialMediaUser.objects.all()[offset:offset + limit]

        # Grab the users either influencers or all
        if influencers_only:
            users = users.filter(is_influencer=influencers_only)

        # Filter out no geo data users
        if not allow_coordinates_null:
            users = users.filter(lat__isnull=False, lon__isnull=False)

        many = True

        # Based on the data_type serialize the users for return
        if data_type == 'user':
            serializer = SocialMediaUserFullNoFriendsSerializer(users, context={'request': request}, many=many)
        elif data_type == 'full':
            serializer = SocialMediaUserFullFriendsSerializer(users, context={'request': request}, many=many)
        elif data_type == 'friend_urls':
            serializer = SocialMediaUserFullFriendsHyperLinkedSerializer(users, context={'request': request}, many=many)
        else:
            serializer = SocialMediaUserHyperLinkListSerializer(users, context={'request': request}, many=many)

        next_offset = offset + limit

        if SocialMediaUser.objects.all().count() <= next_offset:
            next_offset = -1
        elif users.count == 0:
            next_offset = -1

        # Create return dict
        return_dict = dict(
            records=users.count(),
            next_offset=next_offset,
            data=serializer.data
        )

        return Response(return_dict)

    def get_extra_actions(self):
        return []


# ### SOCIAL MEDIA POSTS API ### #


class SocialMediaPosts(APIView):
    """
    Returns a SocialMediaPost object for the provided id.
    """

    @swagger_auto_schema(manual_parameters=[
        openapi.Parameter('data-type', openapi.IN_QUERY, description='Sets type of return for the objects. "post" '
                                                                     'returns full post object minus reposted_by. "url" '
                                                                     'returns just the url to the post. "full" '
                                                                     'returns full data for post and reposted_by. '
                                                                     '"reposted_urls" returns full post object and urls '
                                                                     'for reposted_by.',
                          type=openapi.TYPE_STRING, default='user', enum=['user', 'url', 'full', 'friend_urls']),
    ])
    def get(self, request, pk=-1, format=None):
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

    def get_extra_actions(self):
        return []


class SocialMediaPostsList(APIView):
    """
    Returns a list of SocialMediaPosts
    """

    @swagger_auto_schema(manual_parameters=[
        openapi.Parameter('data-type', openapi.IN_QUERY, description='Sets type of return for the objects. "post" '
                                                                     'returns full post object minus reposted_by. "url" '
                                                                     'returns just the url to the post. "full" '
                                                                     'returns full data for post and reposted_by. '
                                                                     '"reposted_urls" returns full post object and urls '
                                                                     'for reposted_by.',
                          type=openapi.TYPE_STRING, default='post', enum=['post', 'url', 'full', 'resposted_urls']),
        openapi.Parameter('search', openapi.IN_QUERY, description='Searches for a post that contains the specified string.',
                          type=openapi.TYPE_STRING, default=''),
        openapi.Parameter('author-id', openapi.IN_QUERY, description='Limits the posts returned to that of the author-id.',
                          type=openapi.TYPE_INTEGER, default=''),
        openapi.Parameter('limit', openapi.IN_QUERY, description='Limits the return count.',
                          type=openapi.TYPE_INTEGER, default=''),
        openapi.Parameter('offset', openapi.IN_QUERY, description='Offset to start at for the query.',
                          type=openapi.TYPE_INTEGER, default=''),
    ])
    def get(self, request, pk=-1, format=None):
        data_type = request.GET['data-type'] if 'data-type' in request.GET.keys() else None
        limit = int(request.GET['limit']) if 'limit' in request.GET.keys() else MAX_RECORDS_TO_RETURN
        offset = int(request.GET['offset']) if 'offset' in request.GET.keys() else 0
        search = request.GET['search'] if 'search' in request.GET.keys() else None
        author_id = int(request.GET['author-id']) if 'author-id' in request.GET.keys() else None

        if author_id:
            if search:
                search_query = SearchQuery(search)
                search_vector = SearchVector('author', 'hashtags', 'keywords', 'user_mentions', 'reposted_by', 'text',
                                             'sentiment', 'service')

                posts = SocialMediaPost.objects.annotate(
                    search=search_vector
                ).filter(
                    search=search_query,
                    author_id__exact=author_id
                ).order_by('-created_at')[offset:offset + limit]
            else:
                posts = SocialMediaPost.objects.filter(author_id__exact=author_id).order_by('-created_at')[offset:offset + limit]
        else:
            if search:
                search_query = SearchQuery(search)
                search_vector = SearchVector('author', 'hashtags', 'keywords', 'user_mentions', 'reposted_by', 'text',
                                             'sentiment', 'service')

                posts = SocialMediaPost.objects.annotate(
                    search=search_vector
                ).filter(
                    search=search_query,
                ).order_by('-created_at')[offset:offset + limit]
            else:
                posts = SocialMediaPost.objects.all().order_by('-created_at')[offset:offset + limit]


        many = True

        # Based on the data_type serialize the users for return
        if data_type == 'post':
            serializer = SocialMediaPostFullNoRepostedUserInfoSerializer(posts, context={'request': request}, many=many)
        elif data_type == 'full':
            serializer = SocialMediaPostFullRepostedUserInfoFullSerializer(posts, context={'request': request}, many=many)
        elif data_type == 'reposted_urls':
            serializer = SocialMediaPostFullRepostedUserInfoHyperlinkedSerializer(posts, context={'request': request}, many=many)
        else: # 'urls'
            serializer = SocialMediaPostHyperLinkListSerializer(posts, context={'request': request}, many=many)

        next_offset = offset + limit

        if SocialMediaPost.objects.all().count() <= next_offset:
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

    def get_extra_actions(self):
        return []