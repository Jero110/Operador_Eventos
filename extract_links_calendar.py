import requests
from bs4 import BeautifulSoup

def extract_event_links_from_calendar(url):
    # Fetch the webpage content
    response = requests.get(url)
    response.raise_for_status()  # Ensure the request was successful

    # Parse the HTML content
    soup = BeautifulSoup(response.text, 'html.parser')

    # Use CSS selector to find the specific table row
    specific_row = soup.select('body > table > tbody > tr:nth-child(2) > td > table > tbody > tr:nth-child(4)')

    # If the specific row exists, extract the links
    event_links = []
    if specific_row:
        # Find all 'a' tags within the specific row
        links = [a['href'] for a in specific_row[0].find_all('a', href=True)
                 if a['href'].startswith('https://eventos.itam.mx/es/evento/')]
        event_links.extend(links)

    return event_links
