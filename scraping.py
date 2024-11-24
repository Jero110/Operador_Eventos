from extract_links import extract_event_links
from extract_title_description import extract_title_description_and_image
from extract_links_calendar import extract_event_links_from_calendar
from url_imagen import download_image
from event import Event

def scraping():
    # URL to scrape event links
    main_url = "http://boletin.itam.mx/mail/repertorio/2024/47/index.html"
    events = []

    # Step 1: Extract all event links
    event_links = extract_event_links_from_calendar(main_url)

    # Step 2: Extract title and description for each event link
    for link in event_links:
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
        
        # Download image if exists and is not ITAM logo
        if image and "logo-ITAM" not in image:
            download_image(image)
        
        events.append(event)
        print(event)

    return events

if __name__ == "__main__":
    scraping()