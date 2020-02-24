from django.conf.urls import url
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions

from . import views
from .api import SocialMediaUsers, SocialMediaUsersList, SocialMediaPostsList, SocialMediaPosts

schema_view = get_schema_view(
   openapi.Info(
      title="CMI API",
      default_version='v1',
      description="API Docs for CMI Backened"
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    url(r'socialmediauser/$', SocialMediaUsersList.as_view(), name='socialmediauser-list'),
    url(r'socialmediauser/(?P<pk>[0-9]+)/$', SocialMediaUsers.as_view(), name='socialmediauser-detail'),
    url(r'socialmediapost/$', SocialMediaPostsList.as_view(), name='socialmediapost-list'),
    url(r'socialmediapost/(?P<pk>[0-9]+)/$', SocialMediaPosts.as_view(), name='socialmediapost-detail'),
    url(r'^docs/$', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
]

