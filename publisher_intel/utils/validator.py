import logging
import requests
from requests.adapters import HTTPAdapter, Retry

logger = logging.getLogger(__name__)


def get_session() -> requests.Session:
    session = requests.Session()
    retries = Retry(total=3, backoff_factor=0.5, status_forcelist=[500, 502, 503, 504])
    adapter = HTTPAdapter(max_retries=retries)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    session.headers.update({'User-Agent': 'PublisherIntel/1.0', 'Accept-Language': 'en-US,en;q=0.9'})
    return session


def validate_url_live(url: str) -> bool:
    try:
        session = get_session()
        resp = session.head(url, allow_redirects=True, timeout=6)
        # Consider 2xx & 3xx valid
        return resp.status_code < 400
    except Exception as e:
        logger.error(f"HEAD validation failed for {url}: {e}")
        return False
