from django.shortcuts import render, redirect
from bs4 import BeautifulSoup
from .models import NewsArticle
import requests
from django.contrib.auth.decorators import login_required
from . import forms
from django.core.files.base import ContentFile
from urllib.parse import urljoin  
from django.core.files.storage import default_storage
from django.conf import settings
from datetime import datetime
import os
  
# Create your views here.
@login_required(login_url='accounts:login')
def news(request):
    articles = NewsArticle.objects.all().order_by('date_published') 

    if request.method == 'POST':
        # 
        WeiiNews_extract(request)

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

def WeiiNews_extract(request):
    base_url = 'https://www.weii.nl'
    url = base_url + '/nieuws'

    response = requests.get(url)

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        list_items = soup.find('ul', class_='listView-items')

        if list_items:
            items = list_items.find_all('li')
        # look for only the first 5 items in items
        for count, item in enumerate(items[:5]):
            
            link = item.find('a')

            if link:
                href = base_url + link.get('href')
                date_published = link.find('abbr', class_='published').text.strip()
                title = link.find('h3', class_='entry-title').text.strip()

                # Check if an instance with the same URL already exists
                existing_article = NewsArticle.objects.filter(url=href).first()

                if existing_article:
                    print(f"NewsArticle instance with URL '{href}' already exists. Skipping creation.")
                   
                    continue
                
                image = item.find('img')
                if image:
                    image_src = image.get('src')
                    image_url = urljoin(base_url, image_src)

                    image_response = requests.get(image_url)
                    if image_response.status_code == 200:
                        news_article = NewsArticle(
                            title=title,
                            url=href,
                            date_published=date_published,
                            author_id=request.user,
                        )
                        print(image_url)

                        # Save the image content to the thumb field
                        image_content = ContentFile(image_response.content)
                        image_filename = f"image_{count}.jpg"
                        news_article.thumb.save(image_filename, image_content, save=True)

                        try:
                            news_article.save()
                            print(f"saved {count} ")
                        except Exception as e:
                            print(f"Error saving NewsArticle instance: {e}")
                    else:
                        print(f"Failed to download image for URL {href}")
    return

def article_detail(request, slug):
    article = NewsArticle.objects.get()
    return render(request, 'news/news.html', {'article':article})
    #return HttpResponse(slug)


@login_required(login_url='accounts:login') #this is protecting this view and redirect to the login_url
def article_create(request):
    if request.method == 'POST':
        form = forms.CreateArticle(request.POST, request.FILES)
        if form.is_valid():
            instance = form.save(commit=False) #dont commit to the action just yet (False), we will change it and save it after
            instance.author_id = request.user
            instance.save()
            return redirect('news:news')
    else:
        form = forms.CreateArticle()

    return render(request, 'news/article_create.html', {'form':form})

def check_all_media_file_paths():
    media_root = settings.MEDIA_ROOT
    file_paths = []

    # Get all file paths in the media folder using default_storage
    for folder, _, files in default_storage.walk(media_root):
        for file_name in files:
            file_path = os.path.join(folder, file_name)
            file_paths.append(file_path)

    return file_paths

