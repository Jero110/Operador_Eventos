from extract_links import extract_event_links
from extract_title_description import extract_title_description_and_image
from extract_links_calendar import extract_event_links_from_calendar
from url_imagen import download_image
from event import Event
from typing import List
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
import os

def setup_logging():
    """Configure logging for the scraping process."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('scraping.log'),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__)

def save_events_to_file(events: List[Event], filename: str = None) -> str:
    """
    Save events to a text file.
    
    Args:
        events (List[Event]): List of events to save
        filename (str, optional): Custom filename. If None, generates a timestamp-based name
        
    Returns:
        str: Path to the saved file
    """
    if filename is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"events_{timestamp}.txt"
    
    # Create output directory if it doesn't exist
    output_dir = "events_output"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    filepath = os.path.join(output_dir, filename)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(f"Events Report Generated on: {datetime.now()}\n")
        f.write(f"Total Events Found: {len(events)}\n")
        f.write("="*50 + "\n\n")
        
        for i, event in enumerate(events, 1):
            f.write(f"Event #{i}\n")
            f.write(str(event))
            f.write("\n" + "="*50 + "\n\n")
    
    return filepath

def process_single_url(url: str, logger: logging.Logger, download_images: bool = True) -> List[Event]:
    """
    Process a single URL and extract all events from it.
    
    Args:
        url (str): The URL to process
        logger (logging.Logger): Logger instance
        download_images (bool): Whether to download images for events
        
    Returns:
        List[Event]: List of events found in the URL
    """
    events = []
    try:
        # Extract event links from the URL
        logger.info(f"Processing URL: {url}")
        event_links = extract_event_links_from_calendar(url)
        logger.info(f"Found {len(event_links)} event links in {url}")
        
        # Process each event link
        for link in event_links:
            try:
                title, description, image, date, time, location = extract_title_description_and_image(link)
                
                # Create Event object
                event = Event(
                    title=title,
                    description=description,
                    image_url=image,
                    event_url=link,
                    date=date,
                    time=time,
                    location=location
                )
                
                # Download image if enabled and image exists
                if download_images and image and "logo-ITAM" not in image:
                    image_path = download_image(image)
                    if image_path:
                        logger.info(f"Downloaded image for event: {title}")
                elif not download_images:
                    logger.debug(f"Image download skipped for event: {title}")
                
                events.append(event)
                logger.info(f"Successfully processed event: {title}")
                
            except Exception as e:
                logger.error(f"Error processing event link {link}: {str(e)}")
                continue
                
    except Exception as e:
        logger.error(f"Error processing URL {url}: {str(e)}")
    
    return events

def scraping(urls: List[str], download_images: bool = True) -> List[Event]:
    """
    Scrape events from multiple URLs concurrently.
    
    Args:
        urls (List[str]): List of URLs to scrape
        download_images (bool): Whether to download images for events (default: True)
        
    Returns:
        List[Event]: Combined list of all events found
    """
    logger = setup_logging()
    all_events = []
    
    logger.info(f"Starting scraping with image download {'enabled' if download_images else 'disabled'}")
    
    # Use ThreadPoolExecutor for concurrent processing
    with ThreadPoolExecutor(max_workers=5) as executor:
        # Create future tasks for each URL
        future_to_url = {
            executor.submit(process_single_url, url, logger, download_images): url 
            for url in urls
        }
        
        # Process completed tasks
        for future in as_completed(future_to_url):
            url = future_to_url[future]
            try:
                events = future.result()
                all_events.extend(events)
                logger.info(f"Successfully processed URL {url}")
                logger.info(f"Found {len(events)} events")
                
            except Exception as exc:
                logger.error(f"URL {url} generated an exception: {exc}")

    logger.info(f"Scraping completed. Total events found: {len(all_events)}")
    return all_events

if __name__ == "__main__":
    urls_to_scrape = []
    # Generate URLs for range 46-48
    for i in range(34, 48):
        url = f"http://boletin.itam.mx/mail/repertorio/2024/{i}/index.html"
        urls_to_scrape.append(url)
    
    # Scrape events without downloading images
    events_no_images = scraping(urls_to_scrape, download_images=False)
    print(f"\nTotal events found (no images): {len(events_no_images)}")
    
    # Save events to file
    output_file = save_events_to_file(events_no_images)
    print(f"\nEvents have been saved to: {output_file}")