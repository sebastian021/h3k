# from django.urls import path, re_path
# from rest_framework.routers import DefaultRouter
# from .views import NewsDetail, NewsList, ImageViewSet

# router = DefaultRouter()
# router.register(r'news', NewsDetail)

# urlpatterns = [
#     re_path(r'(?P<slug>[-\w]+)/', NewsDetail.as_view(), name='news_detail'),
#     path("", NewsList.as_view(), name="news_list"),
#     path("", ImageViewSet.as_view({'get': 'image'}),  name="image_view")
# ]
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TagViewSet, NewsViewSet, CommentViewSet, ImageViewSet, VideoViewSet

router = DefaultRouter()
router.register(r'tags', TagViewSet)
router.register(r'news', NewsViewSet)
router.register(r'comments', CommentViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('image/', ImageViewSet.as_view({'get': 'list'}), name='image_view'),
    path('video/', VideoViewSet.as_view({'get': 'list'}), name='video_view')
]