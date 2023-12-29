from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login, logout

# Create your views here.
def signup_view(request):
    if request.method == 'POST': #if values are posted 
        form = UserCreationForm(request.POST) #validate values 
        if form.is_valid():
            user = form.save() #save to the database
            login(request, user)
            # log the user in. 
            return redirect('news:news')
    else: #if it is a Get request. 
        form = UserCreationForm()

    return render(request,'accounts/signup.html', {'form':form})

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
                return redirect('news:news')
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