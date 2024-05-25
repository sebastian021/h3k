from rest_framework import viewsets
from .models import News, UploadImage
from .serializers import NewsSerializer , ImageSerializer, VideoSerializer
from rest_framework import generics


class NewsList(generics.ListAPIView):
    queryset = News.objects.filter(status='published')
    serializer_class = NewsSerializer

class NewsDetail(generics.RetrieveAPIView):
    queryset = News.objects.all()
    serializer_class = NewsSerializer
    lookup_field = 'slug'

class ImageViewSet(viewsets.ModelViewSet):
    queryset = UploadImage.objects.all()
    serializer_class = ImageSerializer

class ImageViewSet(viewsets.ModelViewSet):
    queryset = UploadImage.objects.all()
    serializer_class = VideoSerializer

