from django.shortcuts import render

# Create your views here.

def home(request):
    return render(request,'home/home.html')


def boom(request):
    raise Exception("Test 500 error")