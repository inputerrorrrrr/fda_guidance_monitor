from pathlib import Path
import requests
from bs4 import BeautifulSoup
import time
from typing import Optional

BASE_DIR = Path(__file__).resolve().parent

def load_progress(file_path: str = "progress.txt") -> set[str]:
    try:
        with open(BASE_DIR / file_path, 'r') as f:
            return set(line.strip() for line in f if line.strip())
    except FileNotFoundError:
        return set()

def save_progress(file_path: str = "progress.txt", link: str = ""):
    with open(BASE_DIR / file_path, 'a') as f:
        f.write(link + '\n')

def parse_sitemap(url: str, headers: dict, tag_name: str) -> list[tuple[str, Optional[str]]]:

    try:
        response = requests.get(url, timeout=10, headers=headers)
        response.raise_for_status()  # Raise an exception for HTTP errors

        soup = BeautifulSoup(response.content, 'xml')

        result = []

        for url_tag in soup.find_all(tag_name):
            loc_tag = url_tag.find('loc')
            lastmod_tag = url_tag.find('lastmod')

            if loc_tag:
                 link = loc_tag.text.strip()

                 lastmod = lastmod_tag.text.strip() if lastmod_tag else None

                 result.append((link, lastmod))

        time.sleep(30)

        return result

    except requests.exceptions.Timeout:
            print("Timeout")
    except requests.exceptions.HTTPError as e:
            print(f"HTTP error: {e}")
    except Exception as e:
            print(f"An error occurred: {e}")

def fetch_urls() -> set[str]:
    regulatory_urls = []
    headers = {
        f"User-Agent": "FDAinfoBot(Contact: {os.getenv('CONTACT_EMAIL')})"
    }

    urls = []

    url_1st_part = parse_sitemap("https://www.fda.gov/sitemap.xml?page=36", headers, "url")
    urls.extend(url_1st_part)
    url_2nd_part = parse_sitemap("https://www.fda.gov/sitemap.xml?page=37", headers, "url")
    urls.extend(url_2nd_part)

    for url, lastmod in urls:
        if "/regulatory-information/search-fda-guidance-documents/" in url:
            regulatory_urls.append((url, lastmod))
            save_progress("fda_progress.txt", url)

    return regulatory_urls

if __name__ == "__main__":
    progress = load_progress("fda_progress.txt")
    print(f"Loaded {len(progress)} previously processed URLs.")

    urls = fetch_urls()
    print(f"Fetched {len(urls)} regulatory URLs.")
    for url, lastmod in urls:
         print(f"{url}  |  {lastmod}")
         if url not in progress:
            print(f"New URL found!")
            save_progress("fda_progress.txt", url)

