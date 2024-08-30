from django.shortcuts import render, redirect
from .models import NewsArticle
from django.contrib.auth.decorators import login_required
from .news_scrape import WeiiNews_extract, InstallatieNews_extract, EenWInstallatieTechniekNews_extract
from django.core.files.storage import default_storage
from django.conf import settings
import os

# Create your views here.
@login_required(login_url='accounts:login')
def news(request):
   
    if request.method == 'POST':
        delete_all_news(request)
        InstallatieNews_extract(request)
        WeiiNews_extract(request)
        EenWInstallatieTechniekNews_extract(request)
    
    articles = NewsArticle.objects.all().order_by('-date_published_datetime') 
    #print(articles)
    return render(request, 'news/news.html', {'articles': articles})

def delete_all_news(request):
    # Delete all instances of NewsArticle
    NewsArticle.objects.all().delete()
    # You may also want to delete associated media files, assuming they are stored in the 'news_thumbs' folder
     # Delete associated media files (assuming they are stored in the 'news_thumbs' folder)
    media_root = settings.MEDIA_ROOT
    folder_path = os.path.join(media_root, 'news_thumbs')
    
    for file_name in os.listdir(folder_path):
        file_path = os.path.join(folder_path, file_name)
        if os.path.isfile(file_path):
            os.remove(file_path)
    return redirect('news:news')


def check_all_media_file_paths(): # weet niet of ik hier nog iets mee doe?
    media_root = settings.MEDIA_ROOT
    file_paths = []

    # Get all file paths in the media folder using default_storage
    for folder, _, files in default_storage.walk(media_root):
        for file_name in files:
            file_path = os.path.join(folder, file_name)
            file_paths.append(file_path)

    return file_paths
