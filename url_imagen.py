import requests
import os
from urllib.parse import urlparse

def download_image(image_url, save_directory='./downloaded_images'):
    """
    Download an image from a URL and save it to a specified directory.
    
    Parameters:
    image_url (str): The URL of the image to download
    save_directory (str): Directory to save the image (default: 'downloaded_images')
    
    Returns:
    str: Path to the saved image if successful, None if failed
    """
    try:
        # Create the save directory if it doesn't exist
        if not os.path.exists(save_directory):
            os.makedirs(save_directory)
        
        # Get the filename from the URL
        parsed_url = urlparse(image_url)
        filename = os.path.basename(parsed_url.path)
        
        # If no filename is found, use a default name
        if not filename:
            filename = 'downloaded_image.jpg'
        
        # Full path for saving the image
        save_path = os.path.join(save_directory, filename)
        
        # Download the image
        response = requests.get(image_url)
        response.raise_for_status()  # Raise an exception for bad status codes
        
        # Save the image
        with open(save_path, 'wb') as file:
            file.write(response.content)
            
        print(f"Image successfully downloaded: {save_path}")
        return save_path
    
    except requests.exceptions.RequestException as e:
        print(f"Error downloading image: {e}")
        return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

# Example usage
if __name__ == "__main__":
    # Your example URL
    image_url = "https://eventos.itam.mx/sites/all/themes/zmagazine/images/logo-ITAM.png"
    downloaded_path = download_image(image_url)