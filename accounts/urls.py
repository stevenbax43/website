from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('signup/', views.signup_view, name='signup'),  # Assuming you have a view named 'news' in your views.py
    path('login/', views.login_view, name= 'login'),
    path('logout/', views.logout_view, name='logout'),
    # Add other paths as needed for your news app
]