import logging
import time
from typing import List, Dict

from urllib.parse import urljoin, urlparse

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

logger = logging.getLogger(__name__)


def build_driver() -> webdriver.Chrome:
    opts = Options()
    opts.add_argument('--headless=new')
    opts.add_argument('--no-sandbox')
    opts.add_argument('--disable-dev-shm-usage')
    opts.add_argument('--window-size=1400,1000')
    opts.add_argument('--disable-blink-features=AutomationControlled')
    opts.add_argument('--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
    driver = webdriver.Chrome(ChromeDriverManager().install(), options=opts)
    return driver


BAD_PREFIXES = ('#', 'javascript:', 'mailto:')


def scrape_with_selenium(urls: List[str]) -> List[Dict]:
    stories: List[Dict] = []
    driver = build_driver()
    wait = WebDriverWait(driver, 15)
    try:
        for base in urls:
            try:
                driver.get(base)
                # Wait for main content
                try:
                    wait.until(EC.presence_of_element_located((By.TAG_NAME, 'body')))
                except Exception:
                    pass

                links = driver.find_elements(By.CSS_SELECTOR, 'article a, .post a, .news a, a')
                seen = set()
                for el in links:
                    href = el.get_attribute('href')
                    text = (el.text or '').strip()
                    if not href or not text:
                        continue
                    if href.startswith(BAD_PREFIXES):
                        continue
                    # Ignore obvious auth/portal links
                    path = urlparse(href).path or ''
                    if any(p in path for p in ['/portal', '/signin', '/signup', '/login']):
                        continue
                    # Resolve relative
                    href = urljoin(base, href)
                    key = urlparse(href).netloc + urlparse(href).path
                    if key in seen:
                        continue
                    seen.add(key)
                    stories.append({'source': base, 'title': text, 'url': href})
            except Exception as e:
                logger.error(f"Selenium scrape failed for {base}: {e}")
            time.sleep(0.3)
    finally:
        driver.quit()
    return stories
