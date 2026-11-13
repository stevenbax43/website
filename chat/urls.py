from django.urls import path
from . import views

#better safe than sorry to reference to explicit this file
app_name = 'chat'

urlpatterns = [
    path('chatbot/', views.chatbot, name='chatbot'), 
    path('delete/<int:pk>/', views.delete_specific_conversation, name='delete_specific_conversation'),
    path('create-new-chat/', views.create_new_chat, name='create_new_conversation'),  
    path('process-input/', views.process_input, name='process_input'),
    path('chatbot/<int:pk>/', views.chatbot, name='chatbot_with_conversation'), 
]