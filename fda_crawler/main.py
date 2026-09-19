import sitemap_crawler
import content_processor
import article_spider
import url_filter
import email_notifier
from pathlib import Path
import os
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent

load_dotenv(BASE_DIR / ".env")

if __name__ == "__main__":

    output_file = (BASE_DIR / "latest.txt")
    output_file.write_text("", encoding="utf-8")

    regulatory_urls = sitemap_crawler.fetch_urls()

    last_run_time = url_filter.get_last_run_time()
    url_filter.save_current_run_time()

    new_entries = url_filter.filter_new_entries(regulatory_urls, last_run_time)
    latest_entries = url_filter.get_latest_entries(new_entries, top_n=2)

    for url, lastmod in latest_entries:
        print(f"Processing URL: {url} (Last Modified: {lastmod})")
        raw_content = article_spider.fetch_url_content(url)
        if raw_content:
            processed_content = content_processor.parse_h_html(raw_content)
            if not processed_content:
                print(f"Failed to extract content for {url}.")
                continue
            core_text = content_processor.extract_with_context(processed_content)
            summary = content_processor.summarize_with_ai(core_text, url)
            print(f"Summarized successfully!")
        else:
            print(f"Failed to fetch content for {url}.")

        if summary:
            email_notifier.send_email(summary, url, to_email=os.getenv("TO_EMAIL"))
            
        






   



