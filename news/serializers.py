from rest_framework import serializers
from .models import News
from .models import UploadImage, UploadedVideo

class NewsSerializer(serializers.ModelSerializer):
    class Meta:
        model = News
        fields = '__all__'

class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = UploadImage
        fields = '__all__'


class VideoSerializer(serializers.ModelSerializer):
    class Meta:
        model = UploadedVideo
        fields = '__all__'