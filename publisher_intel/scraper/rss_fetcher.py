import logging
import time
from typing import List, Dict

import feedparser
import requests
from requests.adapters import HTTPAdapter, Retry

from utils.date_utils import parse_date, within_days

logger = logging.getLogger(__name__)


def get_session() -> requests.Session:
    session = requests.Session()
    retries = Retry(total=4, backoff_factor=0.5, status_forcelist=[500, 502, 503, 504])
    adapter = HTTPAdapter(max_retries=retries)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    session.headers.update({'User-Agent': 'PublisherIntel/1.0'})
    return session


def fetch_rss(feed_urls: List[str]) -> List[Dict]:
    session = get_session()
    stories: List[Dict] = []
    for url in feed_urls:
        try:
            resp = session.get(url, timeout=10)
            resp.raise_for_status()
            parsed = feedparser.parse(resp.content)
            for entry in parsed.entries:
                link = entry.get('link')
                title = entry.get('title', '')
                published = parse_date(entry)
                if not published:
                    # Missing published date; handled by caller's fallback logic
                    continue
                if not within_days(published, days=7):
                    continue
                stories.append({
                    'source': url,
                    'title': title,
                    'url': link,
                    'published': published.isoformat()
                })
        except Exception as e:
            logger.error(f"RSS fetch failed for {url}: {e}")
            # Caller should fallback to HTML scrape
            continue
        time.sleep(0.2)
    return stories
