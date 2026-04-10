import json
import logging
import os
from datetime import datetime, timezone, timedelta
from typing import List, Dict
from urllib.parse import urlparse

import pandas as pd

from scraper.rss_fetcher import fetch_rss
from ai.classify import is_relevant
from utils.validator import validate_url_live
from utils.date_utils import within_days
from utils.mailer import send_brief_email, render_newsletter_html
from utils.sheets import force_sync_csv
import csv

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(name)s: %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('publisher_intel/logs/errors.log')
    ]
)
logger = logging.getLogger('main')

# Email toggle (off by default). Set ENABLE_EMAIL=1 to turn on.
ENABLE_EMAIL = os.getenv('ENABLE_EMAIL', '0') == '1'
# Google Sheets toggle (on by default). Set ENABLE_GSHEETS=0 to turn off.
ENABLE_GSHEETS = os.getenv('ENABLE_GSHEETS', '1') == '1'


FEED_SOURCES = [
    "https://rss.app/feeds/_pRacWJd71EVOfRl5.xml",
]
HTML_SOURCES = []


def filter_and_validate(stories: List[Dict]) -> List[Dict]:
    filtered = []
    for s in stories:
        url = s.get('url')
        title = s.get('title', '')
        published = s.get('published')
        if not url or not title:
            continue
        # Skip non-http(s)
        if not (url.startswith('http://') or url.startswith('https://')):
            continue
        if published:
            try:
                dt = datetime.fromisoformat(published)
                if not within_days(dt, days=7):
                    continue
            except Exception:
                continue
        if not validate_url_live(url):
            continue
        filtered.append(s)
    return filtered


def process_sources() -> List[Dict]:
    # Step 1: Fetch only from RSS
    rss_stories = fetch_rss(FEED_SOURCES)
    total_fetched = len(rss_stories)

    # Filter + Validate
    valid_stories = filter_and_validate(rss_stories)

    # Classify relevance
    classified = []
    for s in valid_stories:
        rel = is_relevant(s['title'], s['url'])
        s['relevant'] = rel
        classified.append(s)

    # Drop where relevant=false
    relevant_stories = [s for s in classified if s.get('relevant')]

    # Relaxation logic: no HTML retry, only warn if still <5
    if len(relevant_stories) < 5:
        logger.warning('Fewer than 5 relevant stories from RSS feed. Saving results anyway.')

    # Summary report
    total_validated = len(valid_stories)
    total_relevant = len(relevant_stories)
    logger.info(f"Summary: fetched={total_fetched} validated={total_validated} relevant={total_relevant} saved={total_relevant}")

    return relevant_stories


def save_outputs(stories: List[Dict]):
    os.makedirs('publisher_intel/output', exist_ok=True)
    json_path = 'publisher_intel/output/publisher_brief.json'
    csv_path = 'publisher_intel/output/publisher_brief.csv'

    # Save JSON (handles empty list)
    with open(json_path, 'w') as f:
        json.dump(stories, f, indent=2)

    # Save CSV with fixed headers even if empty
    cols = ['source', 'title', 'url', 'published']
    df = pd.DataFrame(stories, columns=cols)
    df.to_csv(csv_path, index=False)

    # Email if we have results (legacy attachments)
    if ENABLE_EMAIL and len(stories) > 0:
        try:
            send_brief_email(
                subject='Publisher Intel — Daily Brief',
                body='Attached: publisher_brief (JSON + CSV).',
                attachments=[json_path, csv_path],
            )
        except Exception as e:
            logger.error(f'Email send failed: {e}')

    # Append to Google Sheet using the CSV contents to guarantee consistency
    spreadsheet_id = os.getenv('GSHEET_ID')  # e.g., 1QLnKe07hQV8ZKnKG2RJKJflLCukJs7oy8ZlI_pbfQhs
    sheet_name = os.getenv('GSHEET_SHEET', 'Sheet1')
    if ENABLE_GSHEETS and spreadsheet_id:
        try:
            csv_df = pd.read_csv(csv_path)
            items = csv_df.to_dict(orient='records')
            # Force full sync so ALL CSV rows are in the sheet
            written = force_sync_csv(spreadsheet_id, sheet_name, items)
            logger.info(f'Force synced {written} rows to Google Sheet {sheet_name}.')
        except Exception as e:
            logger.error(f'Google Sheet sync failed: {e}')


if __name__ == '__main__':
    stories = process_sources()
    save_outputs(stories)
