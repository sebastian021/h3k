from rest_framework import viewsets
from .models import Tag, News, Comment, UploadImage, UploadedVideo 
from .serializers import TagSerializer, NewsSerializer, CommentSerializer, ImageSerializer, VideoSerializer

class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer

class NewsViewSet(viewsets.ModelViewSet):
    queryset = News.objects.all()
    serializer_class = NewsSerializer
    lookup_field = 'slug'  # Use slug as the lookup field
    lookup_url_kwarg = 'slug'  # Use slug as the URL keyword argument

class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer


class ImageViewSet(viewsets.ModelViewSet):
    queryset = UploadImage.objects.all()
    serializer_class = ImageSerializer

class VideoViewSet(viewsets.ModelViewSet):
    queryset = UploadedVideo.objects.all()
    serializer_class = VideoSerializer