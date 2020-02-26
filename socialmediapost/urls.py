from django.conf.urls import url
from rest_framework.routers import DefaultRouter

from socialmediapost.views import SocialMediaPostViewSet

router = DefaultRouter()
router.register(r'socialmedia-post', SocialMediaPostViewSet, basename='socialmedia-post')
urlpatterns = router.urls
