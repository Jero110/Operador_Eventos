import requests
from bs4 import BeautifulSoup

def extract_event_links(url):
    # Fetch the webpage content
    response = requests.get(url)
    response.raise_for_status()  # Ensure the request was successful
    
    # Parse the HTML content
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Find all 'a' tags with the specified URL pattern
    links = [a['href'] for a in soup.find_all('a', href=True) 
             if a['href'].startswith('https://eventos.itam.mx/es/evento/')]
    
    return links

# Example usage
# url = "http://boletin.itam.mx/mail/repertorio/2024/47/index.html"
# event_links = extract_event_links(url)

# print("Extracted Links:")
# for link in event_links:
#     print(link)
