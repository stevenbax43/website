from django.urls import path
from . import views
from .views import CustomPasswordChangeView
app_name = 'accounts'

urlpatterns = [
    path('signup/', views.signup_view, name='signup'),  # Assuming you have a view named 'news' in your views.py
    path('login/', views.login_view, name= 'login'),
    path('logout/', views.logout_view, name='logout'),    
    path('password-change/', CustomPasswordChangeView.as_view(), name='password_change'),
    path('profile/edit/', views.profile_edit, name='profile_edit'),

    # Add other paths as needed for your news app
]