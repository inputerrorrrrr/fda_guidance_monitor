# FDA Guidance Monitor

A Python project that automatically monitors FDA guidance documents, identifies recent updates, summarizes selected documents with AI, and sends the results by email.

## How It Works

The program:

1. Crawls FDA sitemap files and filters for relevant guidance document pages.
2. Compares each page's last edited date with the timestamp of the previous run.
3. Skips pages that were last edited before the previous run.
4. Sorts the remaining guidance documents by their last edited date.
5. Selects the two most recently updated documents.
6. Retrieves the selected document content.
7. Simplifies and cleans the content locally.
8. Uses an AI model to generate concise summaries.
9. Sends the summaries by email.
10. Records the current run time for use in the next run.

## Project Structure

- `main.py` — coordinates the overall workflow
- `sitemap_crawler.py` — crawls FDA sitemap files and filters for relevant guidance document pages
- `url_filter.py` — filters out pages older than the previous run and selects the two most recently updated guidance documents
- `article_spider.py` — retrieves the content of the selected documents
- `content_processor.py` — cleans and simplifies the document content and generates AI summaries
- `email_notifier.py` — sends the final summaries by email

## Features

- FDA sitemap crawling
- Guidance document filtering
- Incremental updates based on the previous run time
- Selection of the two most recently edited documents
- Local text cleaning and simplification
- AI-generated summaries
- Automated email notifications

## What I Learned

Through this project, I practiced working with:

- modular Python programs
- web crawling and sitemap data
- URL filtering and date-based selection
- text extraction and processing
- AI API integration
- environment variables
- automated email notifications
- file-based state tracking
- debugging a multi-step workflow

## Configuration

Private information such as API keys and email credentials is stored in a local `.env` file and is not included in this repository.

The program also uses a local run-time record to track the previous execution time. This file is generated automatically and is not included in the repository.