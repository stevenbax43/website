from django.urls import path
from . import views

#better safe than sorry to reference to explicit this file
app_name = 'chat'

urlpatterns = [
    path('chatbot/', views.chatbot, name='chatbot'),  # Assuming you have a view named 'news' in your views.py
    #path('chat_history/', views.chat_history, name='chat_history')
    # Add other paths as needed for your news app
    path('delete_all_conversations/', views.delete_all_conversations, name='delete_all_conversations'),
]