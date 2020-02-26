from django.contrib.postgres.search import SearchQuery, SearchVector
from django.shortcuts import render
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status, viewsets
from rest_framework.views import APIView
from rest_framework.response import Response

from CMI_Service.settings import MAX_RECORDS_TO_RETURN
from socialmediauser.models import SocialMediaUser
from socialmediauser.serializers import SocialMediaUserHyperLinkListSerializer, SocialMediaUserFullFriendsSerializer, \
    SocialMediaUserFullFriendsHyperLinkedSerializer, SocialMediaUserFullNoFriendsSerializer


class SocialMediaUserViewSet(viewsets.ViewSet):
    """
    Handles the view set for social media users.
    """

    @swagger_auto_schema(operation_description="Retrieve a list of social media users.",
                         manual_parameters=[
                             openapi.Parameter('data-type', openapi.IN_QUERY,
                                               description='Sets type of return for the objects. "user" '
                                                           'returns full user object minus friends. "url" '
                                                           'returns just the url to the user. "full" '
                                                           'returns full data for user and friends. '
                                                           '"friend_urls" returns full user object and urls '
                                                           'for friends.',
                                               type=openapi.TYPE_STRING, default='user',
                                               enum=['user', 'url', 'full', 'friend_urls']),
                             openapi.Parameter('influencers-only', openapi.IN_QUERY,
                                               description='If set to true will only retrieve '
                                                           'influencers.',
                                               type=openapi.TYPE_BOOLEAN, default=False),
                             openapi.Parameter('has-coordinates', openapi.IN_QUERY,
                                               description='If set to true will only retrieve '
                                                           'users with coordinates.',
                                               type=openapi.TYPE_BOOLEAN, default=False),
                             openapi.Parameter('search', openapi.IN_QUERY,
                                               description='Searches for a user that contains the string.',
                                               type=openapi.TYPE_STRING, default=''),
                             openapi.Parameter('limit', openapi.IN_QUERY, description='Limits the return count.',
                                               type=openapi.TYPE_INTEGER, default=''),
                             openapi.Parameter('offset', openapi.IN_QUERY,
                                               description='Offset to start at for the query.',
                                               type=openapi.TYPE_INTEGER, default=''),
                         ])
    def list(self, request):
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

            if influencers_only and not allow_coordinates_null:
                users = SocialMediaUser.objects.annotate(
                    search=search_vector
                ).filter(
                    search=search_query,
                    is_influencer=influencers_only,
                    lat__isnull=False, lon__isnull=False
                )
            elif not allow_coordinates_null:
                users = SocialMediaUser.objects.annotate(
                    search=search_vector
                ).filter(
                    search=search_query,
                    lat__isnull=False, lon__isnull=False
                )
            elif influencers_only:
                users = SocialMediaUser.objects.annotate(
                    search=search_vector
                ).filter(
                    search=search_query,
                    is_influencer=influencers_only,
                )
            else:
                users = SocialMediaUser.objects.annotate(
                    search=search_vector
                ).filter(
                    search=search_query,
                )

        else:
            if influencers_only and not allow_coordinates_null:
                users = SocialMediaUser.objects.filter(is_influencer=influencers_only, lat__isnull=False,
                                                       lon__isnull=False)
            elif not allow_coordinates_null:
                users = SocialMediaUser.objects.filter(lat__isnull=False, lon__isnull=False)
            elif influencers_only:
                users = SocialMediaUser.objects.filter(is_influencer=influencers_only)
            else:
                users = SocialMediaUser.objects.all()

        total_counts = users.count()
        users = users[offset:offset + limit]

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

        if total_counts <= next_offset:
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

    def create(self, request):
        Response({})

    @swagger_auto_schema(operation_description="Retrieve a specific social media user.",
                         manual_parameters=[
                             openapi.Parameter('data-type', openapi.IN_QUERY,
                                               description='Sets type of return for the objects. "user" '
                                                           'returns full user object minus friends. "url" '
                                                           'returns just the url to the user. "full" '
                                                           'returns full data for user and friends. '
                                                           '"friend_urls" returns full user object and urls '
                                                           'for friends.',
                                               type=openapi.TYPE_STRING, default='user',
                                               enum=['user', 'url', 'full', 'friend_urls'])
                         ])
    def retrieve(self, request, pk=None):
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

    def update(self, request, pk=None):
        Response({})

    def partial_update(self, request, pk=None):
        Response({})

    def destroy(self, request, pk=None):
        Response({})
