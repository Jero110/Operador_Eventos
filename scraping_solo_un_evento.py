from event import Event
from extract_links_calendar import extract_event_links_from_calendar
from extract_title_description import extract_title_description_and_image
import os
import logging
from datetime import datetime
import csv
from typing import List, Optional
import requests
from urllib.parse import urlparse
import re

def sanitize_filename(title: str) -> str:
    """
    Convert a string into a safe filename.
    
    Args:
        title (str): String to convert
        
    Returns:
        str: Safe filename
    """
    # Remove invalid filename characters and replace spaces with underscores
    safe_title = re.sub(r'[<>:"/\\|?*]', '', title)
    safe_title = safe_title.replace(' ', '_')
    return safe_title[:100]  # Limit length to avoid too long filenames

def download_image_with_event_name(image_url: str, event_title: str, save_directory: str = 'imagenes') -> Optional[str]:
    """
    Download an image and save it with the event title as part of the filename.
    
    Args:
        image_url (str): URL of the image to download
        event_title (str): Title of the event
        save_directory (str): Directory to save the image
        
    Returns:
        Optional[str]: Path to the saved image if successful, None if failed
    """
    try:
        if not os.path.exists(save_directory):
            os.makedirs(save_directory)
        
        # Get file extension from URL
        parsed_url = urlparse(image_url)
        original_filename = os.path.basename(parsed_url.path)
        file_extension = os.path.splitext(original_filename)[1]
        if not file_extension:
            file_extension = '.jpg'  # Default extension
            
        # Create filename using event title
        safe_title = sanitize_filename(event_title)
        filename = f"{safe_title}{file_extension}"
        save_path = os.path.join(save_directory, filename)
        
        # Download and save image
        response = requests.get(image_url)
        response.raise_for_status()
        
        with open(save_path, 'wb') as file:
            file.write(response.content)
            
        return save_path
    
    except Exception as e:
        print(f"Error downloading image for event '{event_title}': {e}")
        return None

def process_event(url: str, logger: logging.Logger) -> Optional[tuple[Event, str]]:
    """
    Process a single event and its image.
    
    Args:
        url (str): URL of the event
        logger (logging.Logger): Logger instance
    
    Returns:
        Optional[tuple[Event, str]]: Tuple of (Event object, image path) if successful
    """
    try:
        logger.info(f"Processing event URL: {url}")
        
        title, description, image_url, date, time, location = extract_title_description_and_image(url)
        
        # Download image if available
        image_path = None
        if image_url:
            image_path = download_image_with_event_name(image_url, title)
            if image_path:
                logger.info(f"Image downloaded successfully to {image_path}")
            else:
                logger.warning(f"Failed to download image for event: {title}")
        
        event = Event(
            title=title,
            description=description,
            image_url=image_url,
            event_url=url,
            date=date,
            time=time,
            location=location,
            created_at=datetime.now()
        )
        
        return event, image_path
        
    except Exception as e:
        logger.error(f"Error processing event {url}: {str(e)}")
        return None

def save_events_with_images(events_data: List[tuple[Event, str]], filename: str = "calendar_events.csv") -> str:
    """
    Save events and their corresponding image paths to a CSV file.
    
    Args:
        events_data (List[tuple[Event, str]]): List of tuples containing (Event, image_path)
        filename (str): Name of the output file
    
    Returns:
        str: Path to the saved file
    """
    output_dir = "eventos"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    filepath = os.path.join(output_dir, filename)
    
    with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['title', 'date', 'time', 'location', 'description', 'event_url', 'image_url', 'local_image_path']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        writer.writeheader()
        for event, image_path in events_data:
            writer.writerow({
                'title': event.title,
                'date': event.date,
                'time': event.time,
                'location': event.location,
                'description': event.description,
                'event_url': event.event_url,
                'image_url': event.image_url,
                'local_image_path': image_path or 'No image'
            })
    
    return filepath

def scrape_calendar(calendar_url: str):
    """
    Main function to scrape all events from a calendar URL and save their images.
    
    Args:
        calendar_url (str): URL of the calendar to scrape
    """
    logger = setup_logging()
    
    # Create necessary directories
    for directory in ['eventos', 'imagenes']:
        if not os.path.exists(directory):
            os.makedirs(directory)
            logger.info(f"Created directory: {directory}")
    
    try:
        logger.info(f"Extracting event links from calendar: {calendar_url}")
        event_links = extract_event_links_from_calendar(calendar_url)
        logger.info(f"Found {len(event_links)} events in calendar")
        
        # Process each event and keep track of image paths
        processed_events_data = []
        for link in event_links:
            result = process_event(link, logger)
            if result:
                event, image_path = result
                processed_events_data.append((event, image_path))
                logger.info(f"Successfully processed event: {event.title}")
        
        # Save events with their image paths
        if processed_events_data:
            output_file = save_events_with_images(processed_events_data)
            logger.info(f"Saved {len(processed_events_data)} events to: {output_file}")
            logger.info("Calendar processing completed successfully")
        else:
            logger.warning("No events were successfully processed")
            
    except Exception as e:
        logger.error(f"Error processing calendar: {str(e)}")

def setup_logging() -> logging.Logger:
    """Configure logging for the scraping process."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('calendar_scraping.log'),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__)

if __name__ == "__main__":
    # Example calendar URL
    calendar_url = "http://boletin.itam.mx/mail/repertorio/2024/47/index.html"
    scrape_calendar(calendar_url)