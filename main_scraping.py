from extract_links import extract_event_links
from extract_title_description import extract_title_description_and_image
from extract_links_calendar import extract_event_links_from_calendar
from url_imagen import download_image
def main():
    # URL to scrape event links
    main_url = "http://boletin.itam.mx/mail/repertorio/2024/48/index.html"

    # Step 1: Extract all event links
    event_links = extract_event_links_from_calendar(main_url)

    # Step 2: Extract title and description for each event link
    for link in event_links:
        title, description, image = extract_title_description_and_image(link)
        #download_image(image)
        # Check if the image contains "logo-ITAM" and skip if true
        if "logo-ITAM" in image:
            continue
        
        print(f"Title: {title}")
        print(f"Description: {description}")
        print(f"Image: {image}\n")

if __name__ == "__main__":
    main()
