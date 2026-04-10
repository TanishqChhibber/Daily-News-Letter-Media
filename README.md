# Daily News Letter (Media)

A pipeline to fetch, filter, and email a daily newsletter of media/publisher industry news.

---

## Setup

### 1. Clone the Repository

```sh
git clone <your-repo-url>
cd RSS_NEWS_LH2
```

### 2. Python Environment

```sh
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 3. Environment Variables

Create a `.env` file in the project root:

```
# SMTP credentials for sending newsletter
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your_email@gmail.com
SMTP_PASS=your_app_password
FROM_EMAIL=your_email@gmail.com
TO_EMAIL=recipient1@domain.com,recipient2@domain.com

# Google Sheets (optional, for syncing)
GSHEET_ID=your_google_sheet_id
GSHEET_SHEET=Sheet1
```

**Never commit your `.env` or credentials files!**

### 4. Google Sheets Setup (Optional)

See [`publisher_intel/GOOGLE_SHEETS_SETUP.md`](publisher_intel/GOOGLE_SHEETS_SETUP.md) for step-by-step instructions.

---

## Usage

### Run the Pipeline

```sh
python3 publisher_intel/main.py
```

This will:
- Fetch and filter news
- Save results to CSV/JSON
- Sync to Google Sheets (if enabled)
- Email the newsletter (if enabled)

### Send Newsletter Manually

```sh
python3 send_newsletter.py
```

---

## Customization

- Edit `publisher_intel/utils/mailer.py` to change the newsletter HTML style.
- Edit `publisher_intel/ai/classify.py` to adjust relevance criteria.

---

## Security

- **Never commit your `.env` or credentials files.**
- Add `*.json` and `.env` to `.gitignore`.

---

## Branch

This project is on the branch: `Daily-News-Letter-Media`

---

## Support

Contact: tanishq.chhibber@lh2holdings.com
