import requests, os
from dotenv import load_dotenv

# Load environment variables from .env
dotenv_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config/settings/.env')
load_dotenv(dotenv_path)

def EP_API(adr1):
    # Your EP label API key
    api_key = os.environ.get('EP_API_KEY')

    # EP-label API base URL for the test environment
    base_url = 'https://public.ep-online.nl/api/v3/'
    # Specific endpoint for querying based on an address
    endpoint = 'PandEnergielabel/Adres'

    # Full URL for the specific endpoint
    url = f'{base_url}{endpoint}'
    
    postcode = adr1.pcode
    house_number = adr1.hnumber
    addition = adr1.addition

    # Parameters for the address query
    params = {
    'postcode': postcode,  # Replace with the actual postcode
    'huisnummer': house_number, 
    'huisnummertoevoeging': addition,  # Replace with the actual house number
    # Optional: Include additional parameters if needed, such as 'huisletter', 'huisnummertoevoeging', 'detailaanduiding', etc.
    }

    # Optional: Include the API key in the headers if required
    headers = {"Authorization": api_key}

    # Make a request to the EP label website
    response = requests.get(url, params=params, headers=headers)

    if response.status_code == 200:
        label_data = response.json()
        # Request was successful
        adr1.EP_label = label_data[0]['labelLetter']
        #print(adr1.EP_label)
    else:
        # Handle error response
        error_data = response.json()
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
        # Log request details
        #print(f'Request URL: {url}')
        #print(f'Request Headers: {headers}')
        #print(f'Request Data: {input_data}')
        # Check the response status
        response.raise_for_status()

        # Request was successful
        weii_data = response.json()
        adr1.weii = weii_gross = weii_data.get('other', {}).get('WEiiGross')
        #print(weii_gross)
    
        # Process the WEii data as needed

    except requests.exceptions.RequestException as e:
        # Handle error response
        print(f"Error: {e}")

    return adr1

def BAG_data(adr1):
    
    # api-Key provided by BAG to Steven Bax use only for development (NOT production).  
    api_key =  os.environ.get('BAG_API_KEY')

    nummeraanduiding_identificatie = BAG_nummeraanduiding(adr1.pcode, adr1.hnumber, adr1.addition)
    # BAG API base URL for the test environment
    base_url = 'https://api.bag.acceptatie.kadaster.nl/lvbag/individuelebevragingen/v2/'
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
        'X-Api-Key': api_key,
        'Accept-Crs': 'epsg:28992'  # Add the Accept-Crs header
    }
    # Make a GET request to the specific endpoint of the BAG API
    response_2 = requests.get(url=url_2, headers=headers_2, params=params_2)

    # Check if the request was successful (status code 200)
    if response_2.status_code == 200:
        # Print the response content (JSON data)
        response_2_json = response_2.json()
        #extract data from JSON 
        adr1.street  = response_2_json['openbareRuimteNaam']
        adr1.place   = response_2_json['woonplaatsNaam']
        adr1.BAG_surface   = response_2_json['oppervlakte']
        adr1.buildyear   = response_2_json['oorspronkelijkBouwjaar'][0]
        adr1.purpose   = response_2_json['gebruiksdoelen'][0]
        #print(adr1)

    else:
        # Print an error message if the request was not successful
        print(f"Error: {response_2.status_code} - {response_2.text}")
    
    return adr1


def BAG_nummeraanduiding(postcode, nummer, toevoeging):
   
    # api-Key provided by BAG to Steven Bax use only for development (NOT production).  
    api_key = os.environ.get('BAG_API_KEY')

    # BAG API base URL for the test environment
    base_url = 'https://api.bag.acceptatie.kadaster.nl/lvbag/individuelebevragingen/v2/'

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

    # Check if the request was successful (status code 200)
    if response.status_code == 200:
        # Parse JSON response
        response_json = response.json()

        # Check if the actual data is present in the response
        if '_embedded' in response_json and 'nummeraanduidingen' in response_json['_embedded']:
            # Extract the data
            data = response_json['_embedded']['nummeraanduidingen']
            if data:
                nummeraanduiding_identificatie = data[0]['nummeraanduiding']['identificatie']
                #print(f'Nummeraanduiding Identificatie: {nummeraanduiding_identificatie}')
            else:
                print("No data found in the response.")
        else:
            print("No data found in the response.")
    else:
        # Print an error message if the request was not successful
        print(f"Error: {response.status_code} - {response.text}")
    
    return nummeraanduiding_identificatie

