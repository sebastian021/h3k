# Generated by Django 5.0.4 on 2025-02-10 00:48

import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='UploadedVideo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('video', models.FileField(upload_to='videos/')),
                ('created', models.DateTimeField(auto_now_add=True, null=True, verbose_name='تاریخ ثبت ')),
                ('updated', models.DateTimeField(auto_now=True, verbose_name='تاریخ ویرایش')),
                ('publish', models.DateTimeField(default=django.utils.timezone.now, verbose_name='تاریخ انتشار')),
                ('status', models.CharField(choices=[('draft', 'آماده انتشار'), ('published', 'منتشر شده')], default='draft', max_length=60, verbose_name='وضعیت')),
            ],
        ),
        migrations.CreateModel(
            name='UploadImage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(upload_to='images/')),
                ('created', models.DateTimeField(auto_now_add=True, null=True, verbose_name='تاریخ ثبت ')),
                ('updated', models.DateTimeField(auto_now=True, verbose_name='تاریخ ویرایش')),
                ('publish', models.DateTimeField(default=django.utils.timezone.now, verbose_name='تاریخ انتشار')),
                ('status', models.CharField(choices=[('draft', 'آماده انتشار'), ('published', 'منتشر شده')], default='draft', max_length=60, verbose_name='وضعیت')),
            ],
        ),
        migrations.CreateModel(
            name='News',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=60, verbose_name='عنوان')),
                ('slug', models.SlugField(allow_unicode=True, max_length=100, unique=True, verbose_name='لینک')),
                ('seo', models.TextField(blank=True, verbose_name='سئو')),
                ('body', models.TextField(blank=True, max_length=2000, null=True, verbose_name='متن کامل')),
                ('breaftext', models.TextField(blank=True, max_length=400, null=True, verbose_name='خلاصه خبر')),
                ('type', models.CharField(choices=[('image', 'عکس'), ('video', 'ویدیو')], max_length=50)),
                ('media', models.CharField(blank=True, max_length=250, null=True)),
                ('publish', models.DateTimeField(default=django.utils.timezone.now, verbose_name='تاریخ انتشار')),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ثبت ')),
                ('updated', models.DateTimeField(auto_now=True, verbose_name='تاریخ ویرایش')),
                ('status', models.CharField(choices=[('draft', 'آماده انتشار'), ('published', 'منتشر شده')], default='draft', max_length=60, verbose_name='وضعیت')),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('tags', models.ManyToManyField(blank=True, to='news.tag')),
            ],
            options={
                'verbose_name': 'پست',
                'verbose_name_plural': 'پست ها',
            },
        ),
        migrations.CreateModel(
            name='Comment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.TextField()),
                ('likes', models.IntegerField(default=0)),
                ('dislikes', models.IntegerField(default=0)),
                ('reply_to', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='news.comment')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('news', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='news.news')),
            ],
        ),
    ]
