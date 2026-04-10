import os
import csv
import gspread
from google.oauth2.service_account import Credentials

# Configuration
SHEET_ID = "1QLnKe07hQV8ZKnKG2RJKJflLCukJs7oy8ZlI_pbfQhs"  # Google Sheet ID
CREDS_FILE = os.getenv("GOOGLE_APPLICATION_CREDENTIALS", "google-creds.json")  # service account JSON
CSV_FILE = os.getenv("SHEET_CSV_FILE", "publisher_intel/output/publisher_brief.csv")  # exported brief
SHEET_NAME = os.getenv("GSHEET_SHEET", "Sheet1")

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]

if not os.path.exists(CREDS_FILE):
    raise FileNotFoundError(f"Credentials file not found: {CREDS_FILE}")
if not os.path.exists(CSV_FILE):
    raise FileNotFoundError(f"CSV file not found: {CSV_FILE}")

creds = Credentials.from_service_account_file(CREDS_FILE, scopes=SCOPES)
client = gspread.authorize(creds)
worksheet = client.open_by_key(SHEET_ID).worksheet(SHEET_NAME)

# Ensure header
values = worksheet.get_all_values()
if not values:
    worksheet.append_row(["source", "title", "url", "published", "date_added"])  # minimal header
    values = worksheet.get_all_values()

# Collect existing URLs from column C (index 2) skipping header
existing_urls = set()
for row in values[1:]:
    if len(row) >= 3 and row[2]:
        existing_urls.add(row[2])

new_rows = []
from time import strftime
now = strftime("%Y-%m-%d %H:%M:%S")

with open(CSV_FILE, newline="", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for r in reader:
        url = r.get("url", "").strip()
        if not url or url in existing_urls:
            continue
        source = r.get("source", "")
        title = r.get("title", "")
        published = r.get("published", "")
        new_rows.append([source, title, url, published, now])

if new_rows:
    worksheet.append_rows(new_rows, value_input_option="RAW")
    print(f"✅ Appended {len(new_rows)} new rows.")
else:
    print("ℹ️ No new rows to append (all URLs already present or none found).")
