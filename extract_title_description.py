import requests
from bs4 import BeautifulSoup

def extract_title_and_description(url):
    # Fetch the page content
    response = requests.get(url)
    response.raise_for_status()  # Check for HTTP errors
    
    # Parse the HTML content
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Extract the title
    title = soup.title.string if soup.title else "No title found"
    
    # Extract the meta description
    description_meta = soup.find('meta', attrs={'name': 'description'})
    description = description_meta['content'] if description_meta else "No description found"
    
    return title, description

