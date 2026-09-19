from pathlib import Path
import yagmail
import os
from dotenv import load_dotenv
import time

BASE_DIR = Path(__file__).resolve().parent

load_dotenv(BASE_DIR / ".env")

def send_email(content, url, to_email):

    yag = yagmail.SMTP(user = os.getenv("SENDER_EMAIL"), password = os.getenv("EMAIL_PASSWORD"))

    subject = f"FDA Guidance Document Update!"
    body = f"New FDA Guidance Document Update:\n\n{content}\n\nURL: {url}"

    yag.send(to=to_email, subject=subject, contents=body)
    print(f"Email sent to {to_email} for URL: {url}")

    time.sleep(60)