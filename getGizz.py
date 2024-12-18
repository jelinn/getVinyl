#!/usr/bin/env python3
import requests
from bs4 import BeautifulSoup
import sqlite3
import time
import os


# Set discord webhook url in env var
if "DISCORD_WEBHOOK" in os.environ:
        DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK")
else:
    print("Set the URL webhook for discord for notifications\n")
    print("export DISCORD_WEBHOOK=<yourDiscordWebhook>")
    exit()

# Sleep time between scraping
waitTime = 300

# Initialize SQLite database
def initialize_database():
    conn = sqlite3.connect("pdoom.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            link TEXT UNIQUE
        )
    """)
    conn.commit()
    conn.close()

# Fetch products from the database
def fetch_products_from_db():
    conn = sqlite3.connect("pdoom.db")
    cursor = conn.cursor()
    cursor.execute("SELECT link FROM products")
    products = [row[0] for row in cursor.fetchall()]
    conn.close()
    return products

# Save new products to the database
def save_new_products_to_db(new_products):
    conn = sqlite3.connect("pdoom.db")
    cursor = conn.cursor()
    for product in new_products:
        cursor.execute("INSERT OR IGNORE INTO products (link) VALUES (?)", (product['link'],))
    conn.commit()
    conn.close()

# Remove products from the database
def remove_products_from_db(removed_products):
    conn = sqlite3.connect("pdoom.db")
    cursor = conn.cursor()
    for product in removed_products:
        cursor.execute("DELETE FROM products WHERE link = ?", (product,))
    conn.commit()
    conn.close()

# Scrape the website for products
def check_for_new_products(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    product_containers = soup.find_all('div', class_='card__image-wrapper')
    product_info = []
    for product in product_containers:
        link = product.find('a')['href']
        product_info.append({'link': link})
    return product_info

# Send a Discord notification
def send_discord_message(message):
    payload = {"content": message}
    response = requests.post(DISCORD_WEBHOOK_URL, json=payload)

    if response.status_code == 204:
        print("Message sent to Discord!")
    else:
        print(f"Failed to send message. Error: {response.text}")

def main():
    url = 'https://pdoomrecords.com/collections/all'
    initialize_database()

    first_run = True  # Skip notifications on the first run

    while True:
        current_products = check_for_new_products(url)
        print('Checking for new products')

        # Current product links
        current_links = [product['link'] for product in current_products]
        previous_links = fetch_products_from_db()

        # Detect new and removed products
        new_products = [product for product in current_products if product['link'] not in previous_links]
        removed_products = [link for link in previous_links if link not in current_links]

        # Save new products to database
        save_new_products_to_db(new_products)

        # Handle notifications (skip on the first run)
        if not first_run:
            # Notify about new products
            if new_products:
                print("New products found:")
                for product in new_products:
                    print(f"Link: https://pdoomrecords.com{product['link']}")
                    send_discord_message(f"New Product Found - https://pdoomrecords.com{product['link']}")

            # Notify about removed products
            if removed_products:
                print("Products removed:")
                for link in removed_products:
                    print(f"Link: https://pdoomrecords.com{link}")
                    send_discord_message(f"Product Removed - https://pdoomrecords.com{link}")

        # Remove deleted products from the database
        remove_products_from_db(removed_products)

        # Mark the first run as complete
        first_run = False

        time.sleep(waitTime)  # Check every waitTime seconds.

if __name__ == '__main__':
    main()

