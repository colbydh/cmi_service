from django.conf.urls import url
from rest_framework.routers import DefaultRouter

from webarticles.views import NewsSiteViewSet, ArticleViewSet

router = DefaultRouter()
router.register(r'news-site', NewsSiteViewSet, basename='news-site')
router.register(r'news-article', ArticleViewSet, basename='news-article')
urlpatterns = router.urls
