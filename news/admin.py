from django.contrib import admin
from . models import Tag, News, Comment, UploadImage, UploadedVideo

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ['id', 'name']

@admin.register(News)
class NewsAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'created']
    list_filter = ['author', 'created']
    search_fields = ['title', 'body']
    filter_horizontal = ['tags']  # If you want to use a horizontal filter for tags
    # date_hierarchy = 'created_at'  # Remove this line to resolve the error

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['user', 'news', 'text', 'likes', 'dislikes']


class ImageAdmin(admin.ModelAdmin):
    list_display = ('image', 'publish', 'status')
    list_filter = ('publish' , 'status')
    ordering = ['status', 'publish']

class VideoAdmin(admin.ModelAdmin):
    list_display = ('video', 'created', 'updated')
    list_filter = ('publish' , 'status')
    ordering = ['status', '-publish']

admin.site.register(UploadImage, ImageAdmin )
admin.site.register(UploadedVideo, VideoAdmin)
