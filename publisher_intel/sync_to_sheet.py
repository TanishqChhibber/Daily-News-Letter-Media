import os
import pandas as pd
from utils.sheets import force_sync_csv

GSHEET_ID = os.getenv('GSHEET_ID')
GSHEET_SHEET = os.getenv('GSHEET_SHEET', 'Sheet1')
CSV_PATH = 'publisher_intel/output/publisher_brief.csv'

if __name__ == '__main__':
    if not GSHEET_ID:
        raise SystemExit('GSHEET_ID env var not set')
    if not os.path.exists(CSV_PATH):
        raise SystemExit(f'CSV not found: {CSV_PATH}')
    df = pd.read_csv(CSV_PATH)
    rows = df.to_dict(orient='records')
    written = force_sync_csv(GSHEET_ID, GSHEET_SHEET, rows)
    print(f'Force synced {written} rows to Google Sheet {GSHEET_SHEET}.')
