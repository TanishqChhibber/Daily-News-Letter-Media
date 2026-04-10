#!/bin/zsh
# Run the publisher intel pipeline and sync to Google Sheet.
# Requires env vars to be exported (edit below or source a .env file).

# --- ENV VARS ---
export GOOGLE_APPLICATION_CREDENTIALS="/Users/tanishq/RSS_NEWS_LH2/google-creds.json"
export GSHEET_ID="1QLnKe07hQV8ZKnKG2RJKJflLCukJs7oy8ZlI_pbfQhs"
export GSHEET_SHEET="Sheet1"
export ENABLE_GSHEETS=1
# export OPENAI_API_KEY="sk-..."   # uncomment if classification used
# ----------------

cd /Users/tanishq/RSS_NEWS_LH2 || exit 1
/usr/bin/env python3 publisher_intel/main.py
