from extract_links import extract_event_links
from extract_title_description import extract_title_description_and_image
from extract_links_calendar import extract_event_links_from_calendar
from url_imagen import download_image
from event import Event
from tweetllm import tweet  # Import the tweet function
from typing import List
import logging
import csv
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

def process_event_links(urls: List[str], logger: logging.Logger) -> List[dict]:
    """
    Extract and process events from a list of URLs.
    
    Args:
        urls (List[str]): List of URLs to scrape
        logger (logging.Logger): Logger instance
        
    Returns:
        List[dict]: List of dictionaries containing event details and corresponding tweets
    """
    events_with_tweets = []
    
    for url in urls:
        try:
            logger.info(f"Processing URL: {url}")
            event_links = extract_event_links_from_calendar(url)
            logger.info(f"Found {len(event_links)} event links in {url}")
            
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
                    
                    # Generate tweet for the event
                    event_str = f"Title: {event.title}\nDescription: {event.description}\nDate: {event.date}, Time: {event.time}\nLocation: {event.location}\nLink: {event.event_url}"
                    tweet_text = tweet(event_str)
                    
                    # Append event and tweet as a dictionary
                    events_with_tweets.append({
                        "Event": str(event),
                        "Tweet": tweet_text
                    })
                    
                    logger.info(f"Successfully processed event: {event.title}")
                    
                except Exception as e:
                    logger.error(f"Error processing event link {link}: {str(e)}")
                    continue
                
        except Exception as e:
            logger.error(f"Error processing URL {url}: {str(e)}")
    
    return events_with_tweets

def save_events_to_csv(events_with_tweets: List[dict], filename: str = "events_with_tweets.csv") -> str:
    """
    Save events and their corresponding tweets to a CSV file.
    
    Args:
        events_with_tweets (List[dict]): List of dictionaries containing events and tweets
        filename (str): Name of the output file
        
    Returns:
        str: Path to the saved file
    """
    output_dir = "events_output"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    filepath = os.path.join(output_dir, filename)
    
    with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['Event', 'Tweet']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        writer.writeheader()
        for event_with_tweet in events_with_tweets:
            writer.writerow(event_with_tweet)
    
    return filepath

def scraping(urls: List[str]):
    """
    Scrape event details and generate tweets, saving them to a CSV file.
    
    Args:
        urls (List[str]): List of URLs to scrape
    """
    logger = setup_logging()
    events_with_tweets = process_event_links(urls, logger)
    
    output_file = save_events_to_csv(events_with_tweets)
    logger.info(f"Events and tweets have been saved to: {output_file}")

if __name__ == "__main__":
    # Define the range of URLs to scrape
    urls_to_scrape = [f"http://boletin.itam.mx/mail/repertorio/2024/{i}/index.html" for i in range(47, 48)]
    
    scraping(urls_to_scrape)
