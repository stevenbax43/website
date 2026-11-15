import logging

from django.conf import settings
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, PasswordChangeForm
from django.contrib.auth.decorators import user_passes_test, login_required
from django.contrib.auth.views import PasswordChangeView, PasswordResetView
from django.urls import reverse_lazy
from .forms import CustomUserChangeForm

email_logger = logging.getLogger('accounts.email')


class DebugPasswordResetView(PasswordResetView):
    def form_valid(self, form):
        if getattr(settings, 'EMAIL_DEBUG', False):
            eligible_accounts = sum(
                1 for _ in form.get_users(form.cleaned_data['email'])
            )
            email_logger.info(
                'Password reset submitted; eligible_accounts=%d; backend=%s',
                eligible_accounts,
                settings.EMAIL_BACKEND,
            )
        return super().form_valid(form)


# Create your views here.
@user_passes_test(lambda u: u.is_superuser)
def signup_view(request):
    if request.method == 'POST': #if values are posted 
        form = UserCreationForm(request.POST) #validate values 
        if form.is_valid():
            user = form.save() #save to the database
            login(request, user)
            # log the user in. 
            next_param = request.POST.get('next')
            print("Next parameter:", next_param)  # Print the value of 'next' parameter
            if next_param:
                return redirect(next_param)
            else:
                return redirect('tools:tools')
           
    else: #if it is a Get request. 
        form = UserCreationForm()

    return render(request,'accounts/signup.html', {'form':form})

class CustomPasswordChangeView(PasswordChangeView):
    form_class = PasswordChangeForm
    template_name = 'accounts/password_change_form.html'
    success_url = reverse_lazy('accounts:login')


# create a login 
def login_view(request):
    if request.method == 'POST': #if values are posted 
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            #log in the person 
            user = form.get_user()
            login(request, user)
            if 'next' in request.POST:
                return redirect(request.POST.get('next'))
            else:
                return redirect('tools:tools')
    else:
        form = AuthenticationForm()
    return render(request, 'accounts/login.html', {'form':form})

# create a logout 
def logout_view(request):
    if request.method == 'POST': #if values are posted 
        logout(request)
        return redirect('news:news')
    else:
        form = AuthenticationForm()
    return render(request, 'accounts/login.html', {'form':form})

@login_required(login_url='accounts:login')
def profile_edit(request):
    if request.method == 'POST':
        form = CustomUserChangeForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('accounts:profile_edit')
    else:
        form = CustomUserChangeForm(instance=request.user)
    
    return render(request, 'accounts/profile.html', {'form': form})