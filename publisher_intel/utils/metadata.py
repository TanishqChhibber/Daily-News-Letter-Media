import logging
from typing import Tuple, Optional
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter, Retry

logger = logging.getLogger(__name__)


def _session() -> requests.Session:
    s = requests.Session()
    retries = Retry(total=3, backoff_factor=0.4, status_forcelist=[429, 500, 502, 503, 504])
    s.mount('http://', HTTPAdapter(max_retries=retries))
    s.mount('https://', HTTPAdapter(max_retries=retries))
    s.headers.update({
        'User-Agent': 'PublisherIntel/1.0 (+fetch-meta)',
        'Accept-Language': 'en-US,en;q=0.9'
    })
    return s


def fetch_meta(url: str) -> Tuple[Optional[str], Optional[str]]:
    """
    Return (image_url, description) from common meta tags. Resolve relative URLs.
    """
    try:
        s = _session()
        resp = s.get(url, timeout=10)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, 'html.parser')

        def meta_content(attr, value):
            el = soup.find('meta', {attr: value})
            return el.get('content') if el and el.get('content') else None

        img = (meta_content('property', 'og:image') or
               meta_content('name', 'og:image') or
               meta_content('property', 'twitter:image') or
               meta_content('name', 'twitter:image'))
        if img:
            img = urljoin(url, img)

        desc = (meta_content('name', 'description') or
                meta_content('property', 'og:description') or
                meta_content('name', 'twitter:description'))
        return img, desc
    except Exception as e:
        logger.error(f"fetch_meta failed for {url}: {e}")
        return None, None


def bullets_from_description(desc: Optional[str], max_bullets: int = 3) -> str:
    if not desc:
        return ''
    # naive split into short bullets
    text = desc.replace('\n', ' ').strip()
    parts = []
    for splitter in ['. ', ' – ', ' - ']:
        if len(parts) <= 1:
            parts = [p.strip() for p in text.split(splitter) if p.strip()]
    bullets = []
    for p in parts:
        if len(bullets) >= max_bullets:
            break
        bullets.append(p[:200])
    return ' • '.join(bullets)
