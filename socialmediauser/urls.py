from django.conf.urls import url
from rest_framework.routers import DefaultRouter

from socialmediauser.views import SocialMediaUserViewSet

router = DefaultRouter()
router.register(r'socialmedia-user', SocialMediaUserViewSet, basename='socialmedia-user')
urlpatterns = router.urls