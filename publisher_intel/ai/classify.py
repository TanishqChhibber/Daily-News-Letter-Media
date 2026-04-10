import logging
import os
from typing import Dict

from openai import OpenAI

logger = logging.getLogger(__name__)


SYSTEM_PROMPT = (
    "You classify whether a story is relevant to the media industry, especially digital publishing. "
    "\n\n"
    "Return strictly 'true' or 'false' (lowercase). No other text. "
    "\n\n"
    "Return 'true' if the story is about (or has a plausible near-term impact on) any of: "
    "\n"
    "• Publisher traffic/distribution: Google Search/Discover/News, SEO changes, referrals, newsletters, syndication; Yahoo/MSN/Apple News/SmartNews/Newsbreak; Meta/Instagram, TikTok, YouTube, X, Reddit; ranking, policies, product changes, enforcement, outages. "
    "• Monetization: ads (RPM/CPM, formats, brand safety, measurement, privacy/cookies/ID), subscriptions, paywalls, affiliate, commerce, creator monetization, platform revenue shares. "
    "• Newsroom / content operations: AI for writing/editing/research, CMS/workflow/tools, licensing/deals between AI firms and publishers, content policy, moderation, copyright. "
    "• Industry moves: media M&A, consolidation, private equity, publisher partnerships, major creator network deals, strategic pivots, layoffs that signal industry shifts. "
    "• Regulation/legal that affects media/ads/platforms: privacy, competition/antitrust, copyright, platform regulation, data access. "
    "\n"
    "Also return 'true' for broader adtech/martech/creator/streaming/platform industry news if it reasonably affects how publishers get traffic, make money, operate, or plan strategy. "
    "\n"
    "Return 'false' only if it is clearly NOT relevant to the media ecosystem above (e.g., generic brand campaigns/creative awards/celebrity ads/consumer product launches) AND there is no explicit distribution/monetization/platform/publisher impact."
)


def get_client() -> OpenAI:
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        raise RuntimeError('OPENAI_API_KEY not set')
    return OpenAI(api_key=api_key)


def is_relevant(title: str, url: str) -> bool:
    try:
        client = get_client()
        content = f"Title: {title}\nURL: {url}\nRelevant?"
        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": content},
            ],
            temperature=0,
        )
        ans = resp.choices[0].message.content.strip().lower()
        return ans == 'true'
    except Exception as e:
        logger.error(f"OpenAI classify failed: {e}")
        # On failure, mark not relevant to avoid false positives
        return False
