from django.contrib import admin
from django.urls import path, include
from . import views 
from django.conf.urls.static import static
from config.settings import local as settings

#create app name 
app_name = 'home'

urlpatterns = [
    path('admin/', admin.site.urls),
    path('',views.home, name="home"),
    path('about/',views.about),
    path('tools/', include('tools.urls')),
    path('nieuws/', include('news.urls')),
    path('', include('chat.urls')),
    path('accounts/', include('accounts.urls')),
    
]

# Serving static files during development : DEBUG = True
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

