from . import views
from django.urls import path


#better safe than sorry to reference to explicit this file
app_name = 'forum'

urlpatterns = [
    path('', views.topic_list, name='topic_list'),
    path('topic/<int:pk>/', views.topic_detail, name='topic_detail'),
    path('topic/new/', views.create_topic, name='create_topic'),
    path('reply/<int:pk>/delete/', views.delete_reply, name='delete_reply'),
]
