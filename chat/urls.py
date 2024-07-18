from django.urls import path
from . import views

#better safe than sorry to reference to explicit this file
app_name = 'chat'

urlpatterns = [
    path('chatbot/', views.chatbot, name='chatbot'),  # Assuming you have a view named 'news' in your views.py
    path('delete_all_conversations/', views.delete_all_conversations, name='delete_all_conversations'),
    path('save/', views.save_all_conversations, name='save_all_conversations'),
]