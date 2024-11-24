# extract_title_description.py
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import re

def extract_title_description_and_image(url):
    """
    Extract title, description, image, date, time and location from a webpage.
    
    Parameters:
    url (str): The URL of the webpage
    
    Returns:
    tuple: (title, description, image_url, date, time, location)
    """
    # Fetch the page content
    response = requests.get(url)
    response.raise_for_status()
    
    # Parse the HTML content
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Extract the title
    title = soup.title.string if soup.title else "No title found"
    
    # Extract the meta description
    description_meta = soup.find('meta', attrs={'name': 'description'})
    description = description_meta['content'] if description_meta else "No description found"
    
    # Extract the main image
    image_url = None
    for meta in soup.find_all('meta'):
        if meta.get('property') in ['og:image', 'twitter:image']:
            image_url = meta.get('content')
            break
    
    # Extract date and time
    date_div = soup.find('div', id='fecha-evento')
    if date_div:
        # Get the text and split it by <br>
        date_parts = [part.strip() for part in date_div.get_text('\n').split('\n') if part.strip()]
        date = date_parts[0] if date_parts else "No date found"
        time = date_parts[1].replace('De ', '').replace(' h', '') if len(date_parts) > 1 else "No time found"
    else:
        date = "No date found"
        time = "No time found"
    
    # Extract location
    location_div = soup.find('div', id='sede-evento')
    location = location_div.get_text().strip() if location_div else "No location found"
    
    return title, description, image_url, date, time, location