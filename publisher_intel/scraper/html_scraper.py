import logging
import time
from typing import List, Dict
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter, Retry

from utils.date_utils import within_days

logger = logging.getLogger(__name__)


def get_session() -> requests.Session:
    session = requests.Session()
    retries = Retry(total=3, backoff_factor=0.5, status_forcelist=[500, 502, 503, 504])
    adapter = HTTPAdapter(max_retries=retries)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    session.headers.update({
        'User-Agent': 'PublisherIntel/1.0',
        'Accept-Language': 'en-US,en;q=0.9',
    })
    return session


def _is_bad_href(href: str) -> bool:
    if not href:
        return True
    href = href.strip()
    if href.startswith('#'):
        return True
    if href.startswith('javascript:'):
        return True
    if href.startswith('mailto:'):
        return True
    return False


def _is_auth_path(href: str) -> bool:
    parsed = urlparse(href)
    path = parsed.path.lower()
    return any(x in path for x in ['/portal', '/signin', '/signup', '/login'])


def scrape_html(urls: List[str]) -> List[Dict]:
    session = get_session()
    stories: List[Dict] = []
    for url in urls:
        try:
            resp = session.get(url, timeout=10)
            resp.raise_for_status()
            soup = BeautifulSoup(resp.text, 'html.parser')
            candidates = []
            # Prefer likely content areas
            selectors = [
                'article a',
                'section a',
                '.post a',
                '.story a',
                '.news a',
                '.content a',
                'main a',
            ]
            for sel in selectors:
                for a in soup.select(sel):
                    href = a.get('href')
                    text = (a.get_text() or '').strip()
                    if not text or _is_bad_href(href):
                        continue
                    if href.startswith('/'):
                        href = urljoin(url, href)
                    # Require http(s)
                    if not href.startswith('http://') and not href.startswith('https://'):
                        continue
                    if _is_auth_path(href):
                        continue
                    candidates.append({'source': url, 'title': text, 'url': href})

            # Dedupe by normalized URL (scheme+netloc+path)
            seen = set()
            for c in candidates:
                p = urlparse(c['url'])
                key = f"{p.scheme}://{p.netloc}{p.path}"
                if key in seen:
                    continue
                seen.add(key)
                stories.append(c)
        except Exception as e:
            logger.error(f"HTML scrape failed for {url}: {e}")
            continue
        time.sleep(0.3)
    return stories
