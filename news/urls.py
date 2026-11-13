from . import views
from django.urls import path


#better safe than sorry to reference to explicit this file
app_name = 'news'

#extend the /nieuws/ url from base.urls.py
urlpatterns = [
    path('' ,views.news, name='news'),
    #re_path(r'^(?P<slug>[\w-]+)/$', views.article_detail, name='article_detail'),
    path('delete_all_news/', views.delete_all_news, name='delete_all_news'),
    
]
