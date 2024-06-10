from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
urlpatterns = [
    path('admin/', admin.site.urls),
    path('users/', include('users.urls')),
    path('matches/', include('matches.urls')),
    path('', include('news.urls')),
    path('tables/', include('tables.urls')),
    path('fixtures/', include('fixtures.urls')),
    path('<str:league>/teams/', include('teams.urls'))

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)