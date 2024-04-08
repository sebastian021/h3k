from django.urls import path, re_path
from rest_framework.routers import DefaultRouter
from .views import NewsDetail, NewsList, ImageViewSet





router = DefaultRouter()
router.register(r'news', NewsDetail)

urlpatterns = [
    re_path(r'(?P<slug>[-\w]+)/', NewsDetail.as_view(), name='news_detail'),
    path("", NewsList.as_view(), name="news_list"),
    path("", ImageViewSet.as_view({'get': 'image'}),  name="image_view")

]

