from django.db import models
from users.models import User
from django.utils import timezone
from django.utils.text import slugify
from unidecode import unidecode
from django.db.models.signals import post_save
from django.dispatch import receiver
from .utils import create_thumbnails
from users.models import User


class Tag(models.Model):
    name = models.CharField(max_length=100)
    

    def __str__(self):
        return self.name


class News(models.Model):
    STATUS_CHOICES =(
        ('draft' , 'آماده انتشار'),
        ('published', 'منتشر شده'),
    )
    MEDIA_CHOICES =(
        ('image' , 'عکس'),
        ('video', 'ویدیو'),
    )
    title = models.CharField(max_length=60, verbose_name = 'عنوان')    
    slug = models.SlugField(null=False, unique=True, allow_unicode=True, max_length=100, verbose_name = 'لینک')
    seo = models.TextField(blank=True, verbose_name = 'سئو')
    body = models.TextField(max_length=2000, blank=True, null=True, verbose_name = 'متن کامل')
    breaftext = models.TextField(max_length=400, blank=True, null=True, verbose_name = 'خلاصه خبر')
    type = models.CharField(max_length=50, choices=MEDIA_CHOICES)
    media = models.CharField(max_length=250, blank=True, null=True)
    publish = models.DateTimeField(default=timezone.now, verbose_name = 'تاریخ انتشار')
    created = models.DateTimeField(auto_now_add=True, verbose_name = 'تاریخ ثبت ')
    updated = models.DateTimeField(auto_now=True, verbose_name = 'تاریخ ویرایش')
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    status = models.CharField(max_length=60, choices = STATUS_CHOICES , default= 'draft', verbose_name = 'وضعیت')
    tags = models.ManyToManyField(Tag, blank=True)


    def save(self, *args, **kwargs):
        if not self.slug:
            if self.title:
                self.slug = slugify(unidecode(self.title))
        super(News, self).save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("news_detail", args={self.slug})  
    class Meta:
        verbose_name= 'پست'
        verbose_name_plural = 'پست ها'


class UploadImage(models.Model):
    STATUS_CHOICES =(
        ('draft' , 'آماده انتشار'),
        ('published', 'منتشر شده'),
    )
    image = models.ImageField(upload_to='images/')
    created = models.DateTimeField(auto_now_add=True, null=True, verbose_name = 'تاریخ ثبت ')
    updated = models.DateTimeField(auto_now=True, verbose_name = 'تاریخ ویرایش')
    publish = models.DateTimeField(default=timezone.now, verbose_name = 'تاریخ انتشار')
    status = models.CharField(max_length=60, choices = STATUS_CHOICES , default= 'draft', verbose_name = 'وضعیت')

@receiver(post_save, sender=UploadImage)
def generate_thumbnails(sender, instance, created, **kwargs):
    if created:
        create_thumbnails(instance.image.path)


class UploadedVideo(models.Model):
    STATUS_CHOICES =(
        ('draft' , 'آماده انتشار'),
        ('published', 'منتشر شده'),
    )
    video = models.FileField(upload_to='videos/')
    created = models.DateTimeField(auto_now_add=True, null=True, verbose_name = 'تاریخ ثبت ')
    updated = models.DateTimeField(auto_now=True, verbose_name = 'تاریخ ویرایش')
    publish = models.DateTimeField(default=timezone.now, verbose_name = 'تاریخ انتشار')
    status = models.CharField(max_length=60, choices = STATUS_CHOICES , default= 'draft', verbose_name = 'وضعیت')
    

def __str__(self):
    return self.video.name    


class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    news = models.ForeignKey(News, on_delete=models.CASCADE)
    text = models.TextField()
    likes = models.IntegerField(default=0)
    dislikes = models.IntegerField(default=0)
    reply_to = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True)


