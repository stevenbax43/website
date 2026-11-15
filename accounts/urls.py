from django.urls import path
from django.contrib.auth import views as auth_views
from django.urls import reverse_lazy
from . import views
from .views import CustomPasswordChangeView
app_name = 'accounts'

urlpatterns = [
    path('signup/', views.signup_view, name='signup'),  # Assuming you have a view named 'news' in your views.py
    path('login/', views.login_view, name= 'login'),
    path(
        'password-reset/',
        views.DebugPasswordResetView.as_view(
            template_name='accounts/password_reset_form.html',
            email_template_name='accounts/password_reset_email.html',
            html_email_template_name='accounts/password_reset_email_html.html',
            subject_template_name='accounts/password_reset_subject.txt',
            success_url=reverse_lazy('accounts:password_reset_done'),
        ),
        name='password_reset',
    ),
    path(
        'password-reset/done/',
        auth_views.PasswordResetDoneView.as_view(
            template_name='accounts/password_reset_done.html',
        ),
        name='password_reset_done',
    ),
    path(
        'password-reset/<uidb64>/<token>/',
        auth_views.PasswordResetConfirmView.as_view(
            template_name='accounts/password_reset_confirm.html',
            success_url=reverse_lazy('accounts:password_reset_complete'),
        ),
        name='password_reset_confirm',
    ),
    path(
        'password-reset/complete/',
        auth_views.PasswordResetCompleteView.as_view(
            template_name='accounts/password_reset_complete.html',
        ),
        name='password_reset_complete',
    ),
    path('logout/', views.logout_view, name='logout'),    
    path('password-change/', CustomPasswordChangeView.as_view(), name='password_change'),
    path('profile/edit/', views.profile_edit, name='profile_edit'),

    # Add other paths as needed for your news app
]