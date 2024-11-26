from extract_links import extract_event_links
from extract_title_description import extract_title_description_and_image
from extract_links_calendar import extract_event_links_from_calendar
from url_imagen import download_image
from event import Event
from tweetllm import tweet  # Import the tweet function

def scraping():
    # URL to scrape event links
    main_url = "http://boletin.itam.mx/mail/repertorio/2024/47/index.html"
    events = []

    # Open a text file for writing
    with open("events_with_tweets.txt", "w", encoding="utf-8") as file:
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
            
            # Convert the event to a string representation for the tweet query
            event_str = f"Title: {event.title}\nDescription: {event.description}\nDate: {event.date}, Time: {event.time}\nLocation: {event.location}\nLink: {event.event_url}"
            
            # Generate the tweet
            tweet_text = tweet(event_str)

            # Combine the event and its tweet
            event_with_tweet = f"{event}\n\nTweet:\n{tweet_text}\n{'='*40}\n"
            events.append(event_with_tweet)

            # Write to the file
            file.write(event_with_tweet)

            # Download image if exists and is not ITAM logo
            #if image and "logo-ITAM" not in image:
                #download_image(image)

    return events

if __name__ == "__main__":
    scraping()
