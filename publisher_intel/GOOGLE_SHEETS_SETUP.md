# Google Sheets Integration Setup (Publisher Intel)

Follow these steps to make the Google Sheets append work reliably.

## 1. Enable APIs
In Google Cloud Console (project of your choice):
- Enable: Google Sheets API
- Enable: Google Drive API

## 2. Create Service Account
- IAM & Admin > Service Accounts > Create Service Account.
- Grant basic access (no roles beyond needed; Viewer is fine for Sheets usage, but Drive access may require Editor if modifying).
- After creation: Add Key > JSON. Download the file.

## 3. Place Credentials File
Create a folder (recommended):
```
publisher_intel/credentials/
```
Move the downloaded JSON into it and rename for clarity:
```
publisher_intel/credentials/service-account.json
```

## 4. Share the Google Sheet
- Open the target Sheet.
- Click Share.
- Add the service account email (looks like: `name@project.iam.gserviceaccount.com`) with Editor access.

## 5. Set Environment Variables (zsh/macOS)
Add to your shell or `.zshrc`:
```bash
export GOOGLE_APPLICATION_CREDENTIALS="/Users/tanishq/RSS_NEWS_LH2/publisher_intel/credentials/service-account.json"
export GSHEET_ID="1QLnKe07hQV8ZKnKG2RJKJflLCukJs7oy8ZlI_pbfQhs"
export GSHEET_SHEET="Sheet1"  # change if your tab has a different name
```
Reload shell or run:
```bash
source ~/.zshrc
```

## 6. Install Dependencies (already in requirements)
From project root (venv active):
```bash
pip install -r publisher_intel/requirements.txt
```

## 7. Run the Pipeline
```bash
OPENAI_API_KEY="your_openai_key" \
/Users/tanishq/RSS_NEWS_LH2/.venv/bin/python /Users/tanishq/RSS_NEWS_LH2/publisher_intel/main.py
```
After successful run you should see a log line:
```
Appended X new rows to Google Sheet Sheet1.
```

## 8. Verify Column Order
The app assumes columns:
A=source
B=title
C=url
D=published
E=date_added (created by sheets helper)
If starting from an empty Sheet, the helper adds its own header automatically. If you have an existing header, ensure the first 4 columns match the expected order.

## 9. Avoid Committing Secrets
Add to `.gitignore` (create if missing):
```
publisher_intel/credentials/service-account.json
```

## 10. Troubleshooting
- 403 / PERMISSION_DENIED: Ensure the Sheet is shared with the service account email.
- File not found: Check the path in `GOOGLE_APPLICATION_CREDENTIALS`.
- Duplicates: Script skips existing URLs already present in column C.
- Timeout: Retry run; gspread handles transient network issues.

## 11. Manual Script (Optional)
If you use `sheet_update.py`, set:
```python
CSV_FILE = "publisher_intel/output/publisher_brief.csv"
CREDS_FILE = "publisher_intel/credentials/service-account.json"
```

Done. Running the main pipeline now appends new articles automatically.
