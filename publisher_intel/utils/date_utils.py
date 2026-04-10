from datetime import datetime, timezone
from dateutil import parser


def parse_date(entry) -> datetime | None:
    # Try standard RSS date fields
    for key in ['published', 'updated', 'pubDate']:
        val = entry.get(key)
        if val:
            try:
                return parser.parse(val)
            except Exception:
                pass
    # Try entry.get('published_parsed') struct_time
    if entry.get('published_parsed'):
        try:
            return datetime(*entry.published_parsed[:6], tzinfo=timezone.utc)
        except Exception:
            pass
    return None


def within_days(dt: datetime, days: int) -> bool:
    now = datetime.now(timezone.utc)
    if not dt.tzinfo:
        dt = dt.replace(tzinfo=timezone.utc)
    return (now - dt).days <= days
