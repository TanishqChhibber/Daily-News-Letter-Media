import csv
import os
from publisher_intel.utils.mailer import render_newsletter_html, send_brief_email
from datetime import datetime

# Load .env for SMTP credentials
def try_load_dotenv():
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        pass

try_load_dotenv()

CSV_PATH = "publisher_intel/output/publisher_brief.csv"
FROM_EMAIL = os.getenv("FROM_EMAIL", "tanishq.chhibber2003@gmail.com")
TO_EMAILS = [e.strip() for e in os.getenv("TO_EMAIL", "tanishq.chhibber2003@gmail.com").split(",") if e.strip()]

# Read news from CSV
def read_news(csv_path):
    news = []
    with open(csv_path, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Format published date nicely
            try:
                dt = datetime.fromisoformat(row["published"].replace("Z", "+00:00"))
                row["published"] = dt.strftime("%b %d, %Y, %H:%M")
            except Exception:
                pass
            news.append(row)
    return news

def main():
    news = read_news(CSV_PATH)
    if not news:
        print("No news to send.")
        return
    html = render_newsletter_html(news)
    subject = f"📰 Publisher Tech Brief — {datetime.now().strftime('%b %d, %Y')}"
    body = "See the latest news in your inbox."
    send_brief_email(
        subject=subject,
        body=body,
        attachments=[],
        from_email=FROM_EMAIL,
        to_emails=TO_EMAILS,
        html=html
    )
    print("Newsletter sent!")

if __name__ == "__main__":
    main()
