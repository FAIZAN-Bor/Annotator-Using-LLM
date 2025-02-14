import requests
from bs4 import BeautifulSoup
import os
import urllib.parse
import csv
import time
from threading import Thread, Lock

# Base URL
BASE_URL = "https://papers.nips.cc"

# Headers to mimic a real browser
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

lock = Lock()

def get_links_from_page(url):
    """Fetches all links from a given page, skipping broken pages."""
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        response.raise_for_status()
    except requests.HTTPError as e:
        if response.status_code == 500:
            print(f"Skipping {url}: Server error (500)")
            return []  # Skip this page
        print(f"Error accessing {url}: {e}")
        return []

    soup = BeautifulSoup(response.text, "html.parser")
    links = []

    for link in soup.find_all("a", href=True):
        full_link = urllib.parse.urljoin(BASE_URL, link["href"])
        
        # Only keep valid paper links from papers.nips.cc
        if "/paper/" in full_link and "papers.nips.cc" in full_link:
            links.append(full_link)

    return links

def process_link(link, csv_writer, serial_number):
    """Processes a single link to extract authors, abstract, and PDF link."""
    try:
        response = requests.get(link, headers=HEADERS, timeout=10)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Error accessing {link}: {e}")
        return

    soup = BeautifulSoup(response.text, "html.parser")
    authors = [author.text for author in soup.find_all("a", class_="author")]
    abstract_tag = soup.find("h4", string="Abstract")
    abstract = abstract_tag.find_next_sibling("p").text if abstract_tag else "No abstract available"
    paper_button = soup.find("a", string="Paper")
    pdf_url = urllib.parse.urljoin(BASE_URL, paper_button["href"]) if paper_button else "No PDF available"

    with lock:
        csv_writer.writerow([serial_number, ", ".join(authors), abstract, pdf_url])

def main():
    print("Starting scraper...")

    # Open CSV file for writing
    with open("NeurIPS_Papers.csv", mode="w", newline="", encoding="utf-8") as file:
        csv_writer = csv.writer(file)
        csv_writer.writerow(["Serial Number", "Authors Name", "Abstract", "PDF Link"])

        # Step 1: Get links from the homepage
        first_level_links = get_links_from_page(BASE_URL)

        # Step 2: Follow each link to find deeper links
        serial_number = 1
        for link in first_level_links:
            second_level_links = get_links_from_page(link)

            # Step 3: Visit second-level links and extract information
            threads = []
            for second_link in second_level_links:
                thread = Thread(target=process_link, args=(second_link, csv_writer, serial_number))
                thread.start()
                threads.append(thread)
                serial_number += 1
                time.sleep(1)  # Slight delay to avoid overwhelming the server

            for thread in threads:
                thread.join()

    print("CSV file created successfully!")

if __name__ == "__main__":
    main()
