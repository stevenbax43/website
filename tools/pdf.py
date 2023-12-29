from reportlab.pdfgen import canvas
from io import BytesIO
from bs4 import BeautifulSoup
import requests
from urllib.parse import urljoin  
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from django.templatetags.static import static
from django.conf import settings
from django.contrib.staticfiles.finders import find


def generate_pdf(adr1):
    #adr1 = adr1
    #url = google_maps(adr1)
    
    buffer = BytesIO()
    p = canvas.Canvas(buffer)

    # Set starting y-coordinate for the first item
    y_coordinate = 750

    # Add headers
    p.setFont("Helvetica-Bold", 12)
    p.drawString(100, y_coordinate, "Property Details")
    p.setFont("Helvetica", 10)
     # Adjust the y-coordinate for the output data
    y_coordinate -= 20
    # Loop through model fields dynamically
    for field in adr1._meta.fields:
        field_name = field.name.capitalize()
        field_value = str(getattr(adr1, field.name))
        p.drawString(120, y_coordinate, f"{field_name}: {field_value}")
        y_coordinate -= 15

    # Get the absolute path to the image in the static folder
    image_relative_path = 'home/static/images/kropman.png'
    image_path = find(image_relative_path)
    
    if image_path:
        # Draw the image on the PDF
        p.drawInlineImage(image_path, x=100, y=y_coordinate, width=100, height=100)
    else:
        print(f"Image not found: {image_relative_path}")

    p.showPage()
    p.save()

    # Move the buffer's position to the beginning
    buffer.seek(0)

    return buffer

def google_maps(adr1):

    base_url = 'https://www.google.com/maps/'
    initial_url = base_url + "place/" + adr1.street + "+" + adr1.hnumber +",+" + adr1.pcode + "+" + adr1.place
   
    # Set up Chrome options
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    # Set up the Selenium webdriver
    driver = webdriver.Chrome(options=chrome_options)
    driver.get(initial_url)
    # Wait for the cookies button to be clickable
    cookies_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//*[@id='yDmH0d']/c-wiz/div/div/div/div[2]/div[1]/div[3]/div[1]/div[1]/form[1]/div/div/button"))
    )
    cookies_button.click()
    
     # Wait for the URL to change (page to fully load)
    WebDriverWait(driver, 10).until(
        EC.url_changes(initial_url)
    )
    updated_url = driver.current_url
    try:
        img_element = driver.find_element(By.XPATH, "//div[@class='QA0Szd']//img")
        img_src = img_element.get_attribute("src")
        print("Image source:", img_src)
    except:
         print(updated_url)
    driver.quit()
   

  
    return None
