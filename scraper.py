import requests
from bs4 import BeautifulSoup
import os
import urllib.parse
import time
from threading import Thread

# Base URL
BASE_URL = "https://papers.nips.cc"

# Folder to save PDFs
SAVE_FOLDER = "NeurIPS_Papers"
os.makedirs(SAVE_FOLDER, exist_ok=True)

# Headers to mimic a real browser
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

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

def find_paper_button_and_download(links):
    """Finds the 'Paper' button, extracts the PDF link, and downloads it."""
    threads = []
    for link in links:
        thread = Thread(target=process_link, args=(link,))
        thread.start()
        threads.append(thread)
        time.sleep(1)  # Slight delay to avoid overwhelming the server

    for thread in threads:
        thread.join()

def process_link(link):
    """Processes a single link to find the 'Paper' button and download the PDF."""
    try:
        response = requests.get(link, headers=HEADERS, timeout=10)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Error accessing {link}: {e}")
        return

    soup = BeautifulSoup(response.text, "html.parser")
    paper_button = soup.find("a", string="Paper")
    if paper_button:
        pdf_url = urllib.parse.urljoin(BASE_URL, paper_button["href"])
        download_pdf(pdf_url)

def download_pdf(pdf_url):
    """Downloads the PDF file."""
    pdf_name = pdf_url.split("/")[-1]
    pdf_path = os.path.join(SAVE_FOLDER, pdf_name)

    print(f"Downloading: {pdf_name}")
    try:
        response = requests.get(pdf_url, headers=HEADERS, timeout=10)
        response.raise_for_status()
        with open(pdf_path, "wb") as f:
            f.write(response.content)
    except requests.RequestException as e:
        print(f"Failed to download {pdf_url}: {e}")

def main():
    print("Starting scraper...")

    # Step 1: Get links from the homepage
    first_level_links = get_links_from_page(BASE_URL)

    # Step 2: Follow each link to find deeper links
    for link in first_level_links:
        second_level_links = get_links_from_page(link)

        # Step 3: Visit second-level links and find "Paper" buttons
        find_paper_button_and_download(second_level_links)

    print("All PDFs downloaded!")

if __name__ == "__main__":
    main()