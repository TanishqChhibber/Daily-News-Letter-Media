# Publisher Intel

A Python 3.10+ tool to fetch recent articles from publisher RSS feeds and HTML pages, validate URLs live, classify relevance with OpenAI, and export a brief.

## Setup

1. Install Python 3.10+.
2. Create a virtual environment (optional but recommended):
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Set your OpenAI API key:
   ```bash
   export OPENAI_API_KEY=your_api_key_here
   ```

## Run

```bash
python main.py
```

Outputs are saved to `output/publisher_brief.json` and `output/publisher_brief.csv`. Logs are written to `logs/errors.log`.
