import os
import time
from typing import List, Dict

import gspread
from google.oauth2.service_account import Credentials
import logging

SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive',
]

logger = logging.getLogger('sheets')


def _client():
    creds_path = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
    if (not creds_path or not os.path.exists(creds_path)) and os.path.exists('google-creds.json'):
        # Fallback to local file if env var not set
        creds_path = 'google-creds.json'
        logger.info('Using fallback credentials file google-creds.json')
    if not creds_path or not os.path.exists(creds_path):
        raise RuntimeError('Service account credential file missing.')
    creds = Credentials.from_service_account_file(creds_path, scopes=SCOPES)
    return gspread.authorize(creds)


def append_brief_rows(spreadsheet_id: str, sheet_name: str, items: List[Dict]):
    logger.info(f"append_brief_rows called: spreadsheet_id_set={bool(spreadsheet_id)} sheet_name={sheet_name} items_in={len(items)}")
    if not items:
        logger.info('No items provided to append.')
        return 0
    gc = _client()
    sh = gc.open_by_key(spreadsheet_id)
    ws = sh.worksheet(sheet_name)

    replace = os.getenv('GSHEET_REPLACE', '0') == '1'

    if replace:
        ws.clear()
        ws.append_row(['source', 'title', 'url', 'published', 'date_added'])
        existing = set()
        logger.info('Replace mode active: sheet cleared and header written.')
    else:
        try:
            url_col = ws.col_values(3)
            existing = set(url_col[1:])
        except Exception as e:
            logger.warning(f'Failed reading existing URLs: {e}')
            existing = set()

    to_add = []
    now = time.strftime('%Y-%m-%d %H:%M:%S')
    for it in items:
        url = it.get('url')
        if not url or url in existing:
            continue
        row = [
            it.get('source', ''),
            it.get('title', ''),
            url,
            it.get('published', ''),
            now,
        ]
        to_add.append(row)

    logger.info(f"Google Sheets: existing={len(existing)} considered={len(items)} new_rows={len(to_add)} replace={replace}")

    if to_add:
        ws.append_rows(to_add, value_input_option='RAW')
        logger.info('Rows appended successfully.')
    else:
        logger.info('No new rows to append (all duplicates or missing URLs).')
    return len(to_add)


def force_sync_csv(spreadsheet_id: str, sheet_name: str, csv_rows: List[Dict]):
    """Clear the sheet and write all rows from CSV exactly (no dedupe)."""
    logger.info(f'Force sync: rows_in_csv={len(csv_rows)}')
    gc = _client()
    sh = gc.open_by_key(spreadsheet_id)
    try:
        ws = sh.worksheet(sheet_name)
    except Exception:
        ws = sh.add_worksheet(title=sheet_name, rows=100, cols=10)
    ws.clear()
    ws.append_row(['source', 'title', 'url', 'published', 'date_added'])
    now = time.strftime('%Y-%m-%d %H:%M:%S')
    batch = []
    for r in csv_rows:
        batch.append([
            r.get('source',''),
            r.get('title',''),
            r.get('url',''),
            r.get('published',''),
            now,
        ])
    if batch:
        ws.append_rows(batch, value_input_option='RAW')
    logger.info(f'Force sync completed: written={len(batch)}')
    return len(batch)
