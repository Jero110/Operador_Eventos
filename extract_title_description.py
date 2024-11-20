import requests
from bs4 import BeautifulSoup

def extract_title_description_and_image(url):
    """
    Extract title, description, and main image from a webpage.
    
    Parameters:
    url (str): The URL of the webpage
    
    Returns:
    tuple: (title, description, image_url)
    """
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
    
    # Extract the main image (trying multiple common methods)
    image_url = None
    
    # Method 1: Check for image_src link
    image_src_link = soup.find('link', attrs={'rel': 'image_src'})
    if image_src_link and 'href' in image_src_link.attrs:
        image_url = image_src_link['href']
    
    # Method 2: If no image_src, check for og:image
    if not image_url:
        og_image = soup.find('meta', attrs={'property': 'og:image'})
        if og_image and 'content' in og_image.attrs:
            image_url = og_image['content']
    
    # Method 3: If still no image, check for Twitter image
    if not image_url:
        twitter_image = soup.find('meta', attrs={'name': 'twitter:image'})
        if twitter_image and 'content' in twitter_image.attrs:
            image_url = twitter_image['content']
    
    # Method 4: If still no image, look for the first significant image in content
    if not image_url:
        main_images = soup.find_all('img', attrs={'src': True})
        for img in main_images:
            # Skip small images (like icons) by checking for common attributes
            if any(attr in img.attrs for attr in ['width', 'height']):
                try:
                    width = int(img.get('width', 0))
                    height = int(img.get('height', 0))
                    if width > 100 and height > 100:  # Arbitrary size threshold
                        image_url = img['src']
                        break
                except ValueError:
                    continue
            elif img.get('src', '').endswith(('.jpg', '.jpeg', '.png', '.gif')):
                image_url = img['src']
                break
    
    # If no image found
    if not image_url:
        image_url = "No main image found"
    
    # Convert relative URLs to absolute URLs
    if image_url and image_url != "No main image found" and not image_url.startswith(('http://', 'https://')):
        if image_url.startswith('//'):
            image_url = 'https:' + image_url
        else:
            base_url = '/'.join(url.split('/')[:3])  # Get base URL
            image_url = base_url + ('' if image_url.startswith('/') else '/') + image_url
    
    return title, description, image_url

# Example usage
if __name__ == "__main__":
    url = "https://eventos.itam.mx/es/evento/reflexiones-y-propuestas-las-reformas-electorales-tras-el-proceso-2023-2024"  # Replace with your URL
    title, description, image_url = extract_title_description_and_image(url)
    print("Title:", title)
    print("Description:", description)
    print("Main Image URL:", image_url)