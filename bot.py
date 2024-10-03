import requests
from bs4 import BeautifulSoup
import json
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import schedule
import time


from dotenv import load_dotenv
load_dotenv()

import os




# List of URLs to monitor
urls = [
    "https://www.vesteda.com/en/unit-search?...",
    "https://huurportaal.nl/huurwoningen?location=amsterdam&rent=0-1500",
    "https://www.huurwoningen.com/in/amsterdam/?price=0-1500",
    "https://rentola.nl/huurwoningen?location=gemeente-amsterdam&rent=0-1500",
    "https://www.funda.nl/zoeken/huur?selected_area=%5B%22amsterdam%22%5D&object_type=%5B%22apartment%22%5D&price=%22-1500%22",
    "https://www.pararius.nl/huurwoningen/amsterdam/0-1500",
    "https://vbtverhuurmakelaars.nl/woningen",
    "https://amsterdamrentalhomes.com/huuraanbod/",
]

def fetch_listings(url):
    headers = {
        "User-Agent": "Mozilla/5.0"
    }
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.content, 'html.parser')

    listings = []

    # Parsing logic for each website
    if "vesteda.com" in url:
        # Example parsing logic for vesteda.com
        for item in soup.find_all('div', class_='card--list'):
            title = item.find('div', class_='card__content-title').get_text(strip=True)
            price = item.find('div', class_='card__price').get_text(strip=True)
            link = item.find('a', class_='card__link', href=True)['href']
            listings.append({'title': title, 'price': price, 'link': link})
    elif "huurportaal.nl" in url:
        # Parsing logic for huurportaal.nl
        for item in soup.find_all('div', class_='property-listing'):
            title = item.find('a', class_='title').get_text(strip=True)
            price = item.find('div', class_='price').get_text(strip=True)
            link = item.find('a', class_='title', href=True)['href']
            listings.append({'title': title, 'price': price, 'link': link})
    elif "huurwoningen.com" in url:
        # Parsing logic for huurwoningen.com
        for item in soup.find_all('div', class_='property-listing'):
            title = item.find('a', class_='property-title').get_text(strip=True)
            price = item.find('span', class_='property-price').get_text(strip=True)
            link = item.find('a', class_='property-title', href=True)['href']
            listings.append({'title': title, 'price': price, 'link': link})
    elif "rentola.nl" in url:
        # Parsing logic for rentola.nl
        for item in soup.find_all('div', class_='property-item'):
            title = item.find('a', class_='address').get_text(strip=True)
            price = item.find('div', class_='bottom').find('span').get_text(strip=True)
            link = item.find('a', class_='address', href=True)['href']
            listings.append({'title': title, 'price': price, 'link': link})
    elif "funda.nl" in url:
        # Parsing logic for funda.nl
        for item in soup.find_all('li', class_='search-result'):
            title = item.find('h2', class_='search-result__header-title').get_text(strip=True)
            price = item.find('span', class_='search-result-price').get_text(strip=True)
            link = item.find('a', class_='search-result__header-title-col', href=True)['href']
            listings.append({'title': title, 'price': price, 'link': 'https://www.funda.nl' + link})
    elif "pararius.nl" in url:
        # Parsing logic for pararius.nl
        for item in soup.find_all('section', class_='listing-search-item'):
            title = item.find('a', class_='listing-search-item__link--title').get_text(strip=True)
            price = item.find('div', class_='listing-search-item__price').get_text(strip=True)
            link = item.find('a', class_='listing-search-item__link', href=True)['href']
            listings.append({'title': title, 'price': price, 'link': 'https://www.pararius.nl' + link})
    elif "vbtverhuurmakelaars.nl" in url:
        # Parsing logic for vbtverhuurmakelaars.nl
        for item in soup.find_all('div', class_='object-teaser'):
            title = item.find('h2').get_text(strip=True)
            price = item.find('div', class_='price').get_text(strip=True)
            link = item.find('a', href=True)['href']
            listings.append({'title': title, 'price': price, 'link': link})
    elif "amsterdamrentalhomes.com" in url:
        # Parsing logic for amsterdamrentalhomes.com
        for item in soup.find_all('div', class_='property'):
            title = item.find('h3').get_text(strip=True)
            price = item.find('div', class_='price').get_text(strip=True)
            link = item.find('a', href=True)['href']
            listings.append({'title': title, 'price': price, 'link': link})
    else:
        # Default or unknown website parsing
        pass

    return listings

def save_listings(listings, filename='listings.json'):
    with open(filename, 'w') as f:
        json.dump(listings, f)

def load_listings(filename='listings.json'):
    if os.path.exists(filename):
        with open(filename, 'r') as f:
            return json.load(f)
    return []

def get_new_listings(current_listings, previous_listings):
    previous_set = set(item['link'] for item in previous_listings)
    new_listings = [item for item in current_listings if item['link'] not in previous_set]
    return new_listings

def send_email(new_listings):
    # Email configuration
    sender_email = os.getenv("SENDER_EMAIL")
    receiver_email = sender_email  # Assuming you're sending the email to yourself
    password = os.getenv("EMAIL_PASSWORD")
    smtp_server = os.getenv("SMTP_SERVER")
    smtp_port = 587

    recipient_list = ["michele.tufano@outlook.com", "mic.tfn@gmail.com", "lucrezia.bertoni93@gmail.com"]
    # Create the email content
    message = MIMEMultipart("alternative")
    message["Subject"] = "New Housing Listings Available"
    message["From"] = sender_email
    # message["To"] = ", ".join(recipient_list)

        # Get the most recent listing (last item in the list)
    latest_listing = new_listings[-1]

    # Build the HTML content for the last listing only
    html_content = f"""
    <h2>Latest Listing:</h2>
    <ul>
        <li><a href='{latest_listing['link']}'>{latest_listing['title']}</a> - {latest_listing['price']}</li>
    </ul>
    """

    # # Build the HTML content with line breaks
    # html_content = "<h2>New Listings:</h2><ul>"
    # for listing in new_listings:
    #     html_content += (
    #         f"<li><a href='{listing['link']}'>{listing['title']}</a> - {listing['price']}</li>"
    #     )
    # html_content += "</ul>"

    message.attach(MIMEText(html_content, "html"))

    # Send the email
    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()  # Secure the connection
            server.login(sender_email, password)
            for recipient in recipient_list:
                server.sendmail(sender_email, recipient, message.as_string())
        print("Email sent successfully.")
    except Exception as e:
        print(f"Error sending email: {e}")

def main():
    previous_listings = load_listings()
    current_listings = []

    for url in urls:
        listings = fetch_listings(url)
        current_listings.extend(listings)

    new_listings = get_new_listings(current_listings, previous_listings)

    if new_listings:
        email_sent = send_email(new_listings)
        if email_sent:
            print(f"Found {len(new_listings)} new listings. Email sent.")
        else:
            print(f"Found {len(new_listings)} new listings. Failed to send email.")
    else:
        print("No new listings found.")

    save_listings(current_listings)

# Schedule the script to run every 2 minutes

schedule.every(2).minutes.do(main)


if __name__ == "__main__":
    main()  # Run once at startup
    while True:
        schedule.run_pending()
        time.sleep(1)
