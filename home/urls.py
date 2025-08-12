from django.contrib import admin
from django.urls import path, include
from . import views 
from django.conf.urls.static import static
from config.settings import local as settings
from django.views.generic.base import RedirectView
from django.urls import path, reverse
from django.shortcuts import render

#create app name 
app_name = 'home'

urlpatterns = [
    path('admin/', admin.site.urls),
    path('',views.home, name="home"),
    path('tools/', include('tools.urls')),
    path('nieuws/', include('news.urls')),
    path('', include('chat.urls')),
    path('accounts/', include('accounts.urls')),
    path('forum/', include('forum.urls')),
    path('favicon.ico', RedirectView.as_view(url='/static/home/images/favicon.png')),
    path("boom/", views.boom)
]
def _best_tools_url():
    candidates = getattr(settings, "TOOLS_URL_NAMES", ["tools", "tools:index", "core:tools"])
    for name in candidates:
        try:
            return reverse(name)
        except Exception:
            pass
    # Final fallback: a setting or root
    return getattr(settings, "TOOLS_FALLBACK_URL", "/")

def server_error(request):
    return render(request, "home/500.html", {"tools_url": _best_tools_url()}, status=500)

handler500 = server_error
# Serving static files during development : DEBUG = True
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

