from django.contrib import admin
from . models import News, UploadImage, UploadedVideo


class NewsAdmin(admin.ModelAdmin):
    list_display = ('title', 'slug', 'publish', 'status')
    list_filter = ('publish' , 'status')
    search_fields = ( 'title', 'body')
    ordering = ['status', 'publish']
    prepopulated_fields = {'slug' : ('title',)}

class ImageAdmin(admin.ModelAdmin):
    list_display = ('image', 'publish', 'status')
    list_filter = ('publish' , 'status')
    ordering = ['status', 'publish']

class VideoAdmin(admin.ModelAdmin):
    list_display = ('video', 'publish', 'status')
    list_filter = ('publish' , 'status')
    ordering = ['status', 'publish']

admin.site.register(News, NewsAdmin)
admin.site.register(UploadImage, ImageAdmin )
admin.site.register(UploadedVideo, VideoAdmin)
