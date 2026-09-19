from pathlib import Path
import requests
import time
import os
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent

load_dotenv(BASE_DIR / ".env")

headers = {
    "User-Agent": f"FDAinfoBot(Contact: {os.getenv('CONTACT_EMAIL')})"
}

def fetch_url_content(url: str) -> str:
    try:
        response = requests.get(url, timeout=10, headers=headers)
        response.raise_for_status()  # Raise an exception for HTTP errors

        time.sleep(30)  # Sleep for 30 seconds to avoid overwhelming the server

        return response.text

    except requests.exceptions.Timeout:
            print("Timeout")
    except requests.exceptions.HTTPError as e:
            print(f"HTTP error: {e}")
    except Exception as e:
            print(f"An error occurred: {e}")

if __name__ == "__main__":
    test_url = "https://www.fda.gov/regulatory-information/search-fda-guidance-documents/cpg-sec-400210-radiofrequency-identification-feasibility-studies-and-pilot-programs-drugs"
    content = fetch_url_content(test_url)
    if content:
        print("Successfully fetched content.")
        with open(BASE_DIR / "test_content.html", "w", encoding="utf-8") as f:
            f.write(content)
    else:
        print("Failed to fetch content.")