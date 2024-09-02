import requests, os
from dotenv import load_dotenv
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from io import BytesIO
from PyPDF2 import PdfMerger 
from .models import adress
from django.http import FileResponse
from django.utils import timezone
# Load environment variables from .env
dotenv_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config/settings/.env')
load_dotenv(dotenv_path)

def gebouwgegevens(request):
    adr1 = adress()
    EPcolor = "black"
    color_mapping = {'A++': 'dark-green', 'A+':'green','A':'light-green', 'B': 'yellow', 'C': 'orange', 'D': 'dark-orange', 'E': 'light-red','F': 'red'}
    if request.method =='POST':
       
        #get all input values 
        adr1.pcode = request.POST.get('pcode')
        adr1.hnumber = request.POST.get('hnumber')
        adr1.addition = request.POST.get('addition')
       
        adr1 = BAG_data(adr1)
        adr1 = EP_API(adr1)
     
    
    return adr1, EPcolor

def EP_API(adr1):
    # Your EP label API key
    api_key = os.environ.get('EP_API_KEY')
    
    # EP-label API base URL for the test environment
    base_url = 'https://public.ep-online.nl/api/v4/'
    # Specific endpoint for querying based on an address
    endpoint = 'PandEnergielabel/Adres'

    # Full URL for the specific endpoint
    url = f'{base_url}{endpoint}'
    
    # Parameters for the address query
    params = {
    'postcode': adr1.pcode,  # Replace with the actual postcode
    'huisnummer': adr1.hnumber, 
    'huisnummertoevoeging': adr1.addition,  # Replace with the actual house number
    # Optional: Include additional parameters if needed, such as 'huisletter', 'huisnummertoevoeging', 'detailaanduiding', etc.
    }

    # Optional: Include the API key in the headers if required
    headers = {"Authorization": api_key}

    # Make a request to the EP label website
    response = requests.get(url, params=params, headers=headers)
 
    if response.status_code == 200:
        try:
            label_data = response.json()
          
            #print(label_data)
            # Request was successful
            adr1.EP_label = label_data[0]['Energieklasse']
            adr1.EP_surface = label_data[0]['Gebruiksoppervlakte_thermische_zone']
            adr1.EP_energie= label_data[0]['Energiebehoefte']
            adr1.EP_PrimEnergie= label_data[0]['primaireFossieleEnergie']
            adr1.gebouwklasse = label_data[0]['Gebouwklasse']
            adr1.EP_TO = label_data[0]['Temperatuuroverschrijding']
            adr1.EP_warmte = label_data[0]['Warmtebehoefte']
            print(adr1.EP_label)
            print(adr1.energie)
            if adr1.gebouwklasse == 'U':
                adr1.gebouwklasse = 'Utiliteit'
            elif adr1.gebouwklasse == 'W':
                adr1.gebouwklasse = 'Woning'
            else:
                adr1.gebouwklasse = 'onbekend'

        except:
            pass

    else:
        # Handle error response
        error_data = response.json()
        adr1.EP_label = 'Niet gevonden'
        print(f"Error: {response.status_code} - {error_data['title']}")
       
    return adr1

def Weii_API(adr1):
        
    # Replace 'your_api_key' with the actual API key provided by WEii
    api_key = os.environ.get('WEii_API_KEY')

    # WEii API base URL
    base_url = 'https://api.weii.nl/v3/'

    # Specific endpoint for building calculation
    endpoint = 'building'

    # Full URL for the specific endpoint
    url = f'{base_url}{endpoint}'

    #bereken met elektra
    netto_elektra = int(adr1.elektra) - int(adr1.elektra_terug)
    #print(netto_elektra)
    # Example input data, replace it with your actual data
    input_data = {
        "year": int(adr1.calendaryear), # mag niet lager dan 2017 zijn!
        "building": {
            "surfaces": [
                {
                    "buildingType": "Kantoor",
                    "usableSurface": int(adr1.BAG_surface) #make sure to int() to prevent apelstophs: ''
                }
            ],
            "mainMeters": {
                "input": [
                    {
                        "energyType": "Elektriciteit",
                        "volume": int(netto_elektra)
                    },
                    {
                        "energyType": "Aardgas",
                        "volume": int(adr1.gas)
                    }
                ],
            },
        }
    }
    #print(input_data)
    # Optional: Include the API key in the headers if required
    headers = {
        "Authorization": f"Bearer {api_key}"
    }

    try:
        # Make a POST request to the WEii API
        response = requests.post(url, json=input_data, headers=headers)
    
        # Check the response status
        response.raise_for_status()

        # Request was successful
        weii_data = response.json()
        adr1.weii = weii_gross = weii_data.get('other', {}).get('WEiiGross')

    
        # Process the WEii data as needed

    except requests.exceptions.RequestException as e:
        # Handle error response
        print(f"Error: {e}")

    return adr1

def BAG_data(adr1):
    
    # api-Key provided by BAG to Steven Bax use only for development (NOT production).  
    api_key =  os.environ.get('BAG_API_KEY')

    nummeraanduiding_identificatie = BAG_nummeraanduiding(adr1.pcode, adr1.hnumber, adr1.addition)
    #print(nummeraanduiding_identificatie)
    if nummeraanduiding_identificatie is not None:
        
        # BAG API base URL for the test environment
        base_url = 'https://api.bag.kadaster.nl/lvbag/individuelebevragingen/v2/'
        # Specific endpoint (replace with the desired endpoint)
        endpoint_2 = f'adressenuitgebreid/{nummeraanduiding_identificatie}'
        
        # Full URL for the specific endpoint
        url_2 = f'{base_url}{endpoint_2}' 
        
        # Parameters for the request (replace with actual parameters)
        params_2 = {
            'inclusiefEindStatus': 'true'
        }
        headers_2 = {
            'Accept': 'application/hal+json',
            'Accept-Crs': 'epsg:28992',  # Add the Accept-Crs header
            'X-Api-Key': api_key,
        }
        #print(headers_2)
        # Make a GET request to the specific endpoint of the BAG API
        response_2 = requests.get(url=url_2, headers=headers_2, params=params_2)
       
        # Check if the request was successful (status code 200)
        if response_2.status_code == 200:
            # Print the response content (JSON data)
            response_2_json = response_2.json()
           
            #extract data from JSON 
            adr1.street  = response_2_json['openbareRuimteNaam'] #straatnaam
            adr1.place   = response_2_json['woonplaatsNaam']
            adr1.BAG_surface   = response_2_json['oppervlakte']
            adr1.buildyear   = response_2_json['oorspronkelijkBouwjaar'][0]
            adr1.purpose   = response_2_json['gebruiksdoelen'][0]
            #print(adr1.street)

        else:
            # Print an error message if the request was not successful
            print(f"Error: {response_2.status_code} - {response_2.text}")
    else:
        adr1.street = "Adres niet gevonden"
    return adr1


def BAG_nummeraanduiding(postcode, nummer, toevoeging):
   
    # api-Key provided by BAG to Steven Bax use only for development (NOT production).  
    api_key = os.environ.get('BAG_API_KEY')
    
    # BAG API base URL for the test environment
    base_url = 'https://api.bag.kadaster.nl/lvbag/individuelebevragingen/v2/'

    # Specific endpoint for querying based on various parameters
    endpoint = 'nummeraanduidingen'

    # Full URL for the specific endpoint
    url = f'{base_url}{endpoint}'
    
    # Parameters for the request
    params = {
        'postcode': postcode,
        'huisnummer': nummer + toevoeging,
        'exacteMatch': True,
        'page': 1,
        'pageSize': 20
    }

    # Headers with the API key and accept header
    headers = {
        'Accept': 'application/hal+json',
        'X-Api-Key': api_key
    }

    # Make a GET request to the specific endpoint of the BAG API with parameters
    response = requests.get(url=url, headers=headers, params=params)
  
    nummeraanduiding_identificatie = None #default value 
    # Check if the request was successful (status code 200)
    if response.status_code == 200:
        # Parse JSON response
        response_json = response.json()
        #print(response_json)
        # Check if the actual data is present in the response
        if '_embedded' in response_json and 'nummeraanduidingen' in response_json['_embedded']:
            # Extract the data
            data = response_json['_embedded']['nummeraanduidingen']
            if data:
                nummeraanduiding_identificatie = data[0]['nummeraanduiding']['identificatie']
                #print(f'Nummeraanduiding Identificatie: {nummeraanduiding_identificatie}')
            else:
                print("No data found in the response2.")
        else:
            print("No data found in the response1.")
    else:
        # Print an error message if the request was not successful
        print(f"Error: {response.status_code} - {response.text}")
        
    
    return nummeraanduiding_identificatie



def generate_pdf(adr1):
    #create a buffer to store dynamically generated PDF content
    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)

    # Set starting y-coordinate for the first item
    y_coordinate = 700

    # Add headers
    p.setFont("Helvetica-Bold", 12)
    p.drawString(100, y_coordinate, "Gebouweigenschappen")
    p.setFont("Helvetica", 10)
    # Adjust the y-coordinate for the output data
    y_coordinate -= 40

    postcode = adr1.pcode

    if postcode:
        # Draw the formatted time
        formatted_time = adr1.date.strftime("%H:%M %d-%b-%Y ")
        p.drawString(100, y_coordinate, f"Aangemaakt op: {formatted_time} ")
        y_coordinate -= 15
        
        # Draw the author
        p.setFont("Helvetica", 10)
        p.drawString(100, y_coordinate, f"Ingevuld door: {adr1.author_id}")
        y_coordinate -= 50
        
        # Draw the filled data
        p.setFont("Helvetica-Bold", 10)
        filled_data = f"Ingevulde gegevens"
        p.drawString(100, y_coordinate, filled_data)
        p.setFont("Helvetica", 10)
        y_coordinate -= 15
        p.drawString(100, y_coordinate, f"Postcode + huisnummer: {adr1.pcode}, {adr1.hnumber}{adr1.addition} ")
        y_coordinate -= 15
        p.drawString(100, y_coordinate, f"Elektra verbruik ({adr1.calendaryear}): {adr1.elektra}kWh en {adr1.elektra_terug}kWh teruggeleverd")
        y_coordinate -= 15
        p.drawString(100, y_coordinate, f"Gas verbruik ({adr1.calendaryear}): {adr1.gas}m³")
        y_coordinate -= 50

        # Underline the word "Gevonden"
        p.setFont("Helvetica-Bold", 10)
        p.drawString(100, y_coordinate, "Gevonden")
        y_coordinate -= 15
        p.setFont("Helvetica", 10)
        # Draw the found address
        found_address = f"Adres: {adr1.street} {adr1.hnumber}{adr1.addition}, {adr1.pcode} {adr1.place}"
        p.drawString(100, y_coordinate, found_address)
        y_coordinate -= 15
        
        # Draw other details
        p.drawString(100, y_coordinate, f"Gebouwoppervlakte: {adr1.BAG_surface} m²")
        y_coordinate -= 15
        p.drawString(100, y_coordinate, f"EP-label: {adr1.EP_label}")
        y_coordinate -= 15
        p.drawString(100, y_coordinate, f"Bouwjaar: {adr1.buildyear}")
        y_coordinate -= 15
        p.drawString(100, y_coordinate, f"Gebruiksdoel: {adr1.purpose}")
        y_coordinate -= 15
        p.drawString(100, y_coordinate, f"Werkelijk Energie Intensiteit Indicator (WEII): {adr1.weii}")
        y_coordinate -= 50
    
    def add_image_with_link(p, image_path, x, y, width, height, link_url):
        # Draw the image on the canvas
        p.drawInlineImage(image_path, x, y, width=width, height=height)

        # Define the clickable area and link URL
        p.linkURL(link_url, (x, y, x + width, y + height))

    
    add_image_with_link(p, "tools/static/tools/images/BAGkadaster-logo.png", 100, 75, width=100, height=90, link_url="https://bagviewer.kadaster.nl/lvbag/bag-viewer/?zoomlevel=1")
    add_image_with_link(p, "tools/static/tools/images/label-u-bouw.jpg", 250, 75, width=100, height=75, link_url="https://www.ep-online.nl/")
    add_image_with_link(p, "tools/static/tools/images/WEii-logo.png", 400, 75, width=100, height=50, link_url="https://www.weii.nl/rekentool")
    
    # Loop through model fields dynamically
    #for field in adr1._meta.fields:
     #   field_name = field.name.capitalize()
      #  field_value = str(getattr(adr1, field.name))
     #   p.drawString(120, y_coordinate, f"{field_name}: {field_value}")
     #   y_coordinate -= 15

    #save to a temporary file 
    p.showPage()
    p.save()

    # Move the buffer's position to the beginning
    buffer.seek(0)
    
    # Create PdfMerger object
    pdf_merger = PdfMerger()
    # Append existing PDF to PdfMerger object
    pdf_merger.append('tools/static/tools/files/default_gebouwgegevens.pdf') #check if in production works as well? 
    
        
     # Append dynamically generated PDF to PdfMerger object
    pdf_merger.append(BytesIO(buffer.read()))
    
     # Create a BytesIO buffer to store the merged PDF
    merged_pdf_buffer = BytesIO()
    
    # Write the merged PDF to the buffer
    pdf_merger.write(merged_pdf_buffer)

    # Reset buffer position before returning
    merged_pdf_buffer.seek(0)

    return merged_pdf_buffer

