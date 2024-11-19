from extract_links import extract_event_links
from extract_title_description import extract_title_and_description

def main():
    # URL to scrape event links
    main_url = "http://boletin.itam.mx/mail/repertorio/2024/47/index.html"
    
    # Step 1: Extract all event links
    #print("Extracting event links...")
    event_links = extract_event_links(main_url)
    #print("\n".join(event_links))
    # Step 2: Extract title and description for each event link
    for link in event_links:
       # print(f"Fetching data for: {link}")
        title, description = extract_title_and_description(link)
        print(f"Title: {title}")
        print(f"Description: {description}\n")

if __name__ == "__main__":
    main()
