
from bs4 import BeautifulSoup
from .models import NewsArticle
import requests
from django.core.files.base import ContentFile
from urllib.parse import urljoin  
import re, pytz
from datetime import datetime

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
                published_text = link.find('abbr', class_='published').text.strip()
                title = link.find('h3', class_='entry-title').text.strip()
                #get published_date in datetime 
                date_link = link.find('span', class_='value-title')
                datetime_title = date_link.get('title', '') if date_link else 'No datetime found'
                
                
                
                # Check if an instance with the same URL already exists
                existing_article = NewsArticle.objects.filter(url=href).first()

                if existing_article:
                    print(f"NewsArticle instance with URL '{href}' already exists. Skipping creation.")
                   
                    continue
                
                image = item.find('img')
                if image:
                    image_src = image.get('src')
                    image_url = urljoin(base_url, image_src)
                    
                    #zonder foto sla de articelen niet op
                    image_response = requests.get(image_url)
                    if image_response.status_code == 200:
                        news_article = NewsArticle(
                            title=title,
                            url=href,
                            date_published_text=published_text,
                            date_published_datetime = datetime_title,
                            author_id=request.user,
                        )
                        #print(image_url)

                        # Save the image content to the thumb field
                        image_content = ContentFile(image_response.content)
                        image_filename = f"Weii_{count}.jpg"
                        news_article.thumb.save(image_filename, image_content, save=True)

                        try:
                            news_article.save()
                            #print(f"saved {count} ")
                        except Exception as e:
                            print(f"Error saving NewsArticle instance: {e}")
                    else:
                        print(f"Failed to download image for URL {href}")
    return

# def article_detail(request):
#     article = NewsArticle.objects.get()
#     return render(request, 'news/news.html', {'article':article})
#     #return HttpResponse(slug)

def InstallatieNews_extract(request):
    
    base_url = 'https://www.installatie.nl/'
    url = base_url + '/categorie/nieuws/'
  
    response = requests.get(url)
 

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        articles = soup.select('article.post-list') if soup else []
        # look for first 5 valid article in articles 
        saved_count = 0
        for article in articles:
            if saved_count >= 5:
                break  # Exit the loop once 5 articles have been saved
            
            #get title of article 
            title = article.find('h2','').text.strip()
            link = article.find('a')
            #print(link)
            if link:
                href = link.get('href')
                
                #Check if an instance with the same URL already exists
                existing_article = NewsArticle.objects.filter(url=href).first()
               
                if existing_article:
                    print(f"NewsArticle instance with URL '{href}' already exists. Skipping creation.")
                    continue
              
                
                #get date published van een andere URL website 
                response_article = requests.get(href)
                if response.status_code == 200:
                    soup_article = BeautifulSoup(response_article.text, 'html.parser')
                     #check of alleen niet-premium accounts
                    blur_premium = soup_article.find('div', class_='emgp-relative')
                    if blur_premium:
                        continue

                    entry_meta = soup_article.find('div', class_='entry-meta')
                    
                    if entry_meta:
                        date_tag = entry_meta.find('time', class_='entry-date published updated')
                        publication_date = date_tag.get_text(strip=True) if date_tag else 'No publication date'
                        datetime_title = date_tag.get('datetime', '') if date_tag else 'No datetime found'
                    else:
                        publication_date = 'No publication date'
                        
                    #print(f"Publication Date: {publication_date}")              
                image = article.find('div', class_='post-image')
                if image:
                    style_attr = image.get('style', '')
                    match = re.search(r'url\(([^)]+)\)', style_attr)
                    if match:
                        image_url = match.group(1).strip('\'"')  # Remove quotes if they exist
                        image_response = requests.get(image_url)
                        if image_response.status_code == 200:
                            news_article = NewsArticle(
                                title=title,
                                url=href,
                                date_published_text=publication_date,
                                date_published_datetime=datetime_title,
                                author_id=request.user,
                            )
                            #print(image_url)
                            
                            # Save the image content to the thumb field
                            image_content = ContentFile(image_response.content)
                            image_filename = f"Installatie_{saved_count}.jpg"
                            news_article.thumb.save(image_filename, image_content, save=True)
                            if blur_premium:
                                pass
                            else:
                                try:
                                    news_article.save()
                                    saved_count += 1
                                    #print(f"saved {count} ")
                                except Exception as e:
                                    print(f"Error saving NewsArticle instance: {e}")
                        else:
                            print(f"Failed to download image for URL {href}")
                   
    
                
    return 


def EenWInstallatieTechniekNews_extract(request):
    base_url = 'https://www.ew-installatietechniek.nl'
    url = base_url + '/home'
    
    response = requests.get(url)
    

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        #print(soup)
        article_div = soup.find('div', class_='pages-overview')

        articles = article_div.find_all('article', class_='item page-1') if article_div else []
        #print(articles)
        #look for first 5 valid article in articles 
        saved_count = 0
        for article in articles:
            if saved_count >= 5:
                break  # Exit the loop once 5 articles have been saved
            
            #get title of article 
            title_div = article.find('div',class_='caption')
            h3_tag =  title_div.find('h3') if title_div else None
            title = h3_tag.get_text(strip=True) if h3_tag else 'No <h3> tag found'
       
            link = title_div.find('a')
            #print(link)
            if link:
                href_base = link.get('href')
                href  = base_url + href_base
                
                #Check if an instance with the same URL already exists
                existing_article = NewsArticle.objects.filter(url=href).first()
               
                if existing_article:
                    print(f"NewsArticle instance with URL '{href}' already exists. Skipping creation.")
                    continue
                
                #get date published van een andere URL website 
                response_article = requests.get(href)
                if response.status_code == 200:
                    soup_article = BeautifulSoup(response_article.text, 'html.parser')
                    #print(soup_article)
                    time_element = soup_article.find('span', class_='edition') 
                    date_text = time_element.get_text(strip=True) if time_element else None
                    # convert to dateobject          
                    try:
                        month_mapping = {
                            "januari": "01",
                            "februari": "02",
                            "maart": "03",
                            "april": "04",
                            "mei": "05",
                            "juni": "06",
                            "juli": "07",
                            "augustus": "08",
                            "september": "09",
                            "oktober": "10",
                            "november": "11",
                            "december": "12"
                        }
                        day, month_name, year = date_text.split()
                        month = month_mapping[month_name]
                        new_date_string = f"{day}-{month}-{year}"
                        naive_date_obj = datetime.strptime(new_date_string, "%d-%m-%Y")
                        timezone = pytz.timezone('Europe/Amsterdam')
                        date_obj = timezone.localize(naive_date_obj)
                        #date_obj = datetime.strptime(new_date_string, "%d-%m-%Y")
                        #print(f"Extracted Date (as datetime object): {date_obj}")
                    except ValueError as e:
                        print(f"Error parsing date: {e}")
                    
                #print(f"Publication Date: {publication_date}")              
                figure_element = soup_article.find('main').find('figure')
                #print(figure_element)
                img_element = figure_element.find('img')
                if img_element:
                    img_src = img_element['src'] if img_element else None
                    full_img_url = urljoin(base_url, img_src) if img_src else None
                                         
                    image_response = requests.get(full_img_url)
                    
                    if image_response.status_code == 200:
                        news_article = NewsArticle(
                            title=title,
                            url=href,
                            date_published_text=date_text,
                            date_published_datetime=date_obj,
                            author_id=request.user,
                        )
                        #print(image_url)
                        
                        # Save the image content to the thumb field
                        image_content = ContentFile(image_response.content)
                        #print(image_content)
                        image_filename = f"EenWInstallatieTechniek_{saved_count}.jpg"
                        news_article.thumb.save(image_filename, image_content, save=True)
                        
                        try:
                            news_article.save()
                            saved_count += 1
                        except Exception as e:
                            print(f"Error saving NewsArticle instance: {e}")
                    else:
                        print(f"Failed to download image for URL E&W ")
                        
    
                
    return 