import os
import csv
import sys
from datetime import datetime
# Ensure project root is on path
APP_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(APP_DIR, '..'))
if ROOT not in sys.path:
    sys.path.append(ROOT)

from flask import Flask, render_template, send_from_directory
from utils.metadata import fetch_meta, bullets_from_description

OUTPUT_DIR = os.path.join(ROOT, 'output')

app = Flask(__name__, template_folder=os.path.join(APP_DIR, 'templates'), static_folder=os.path.join(APP_DIR, 'static'))


def load_items(limit=30):
    items = []
    path = os.path.join(OUTPUT_DIR, 'publisher_brief.csv')
    if not os.path.exists(path):
        return items
    with open(path, newline='') as f:
        reader = csv.DictReader(f)
        for row in reader:
            url = row.get('url')
            img, desc = fetch_meta(url) if url else (None, None)
            row['image'] = img or ''
            row['bullets'] = bullets_from_description(desc)
            items.append(row)
            if len(items) >= limit:
                break
    return items


@app.route('/')
def index():
    items = load_items()
    return render_template('index.html', news=items)


@app.route('/static/<path:filename>')
def static_files(filename):
    return send_from_directory(os.path.join(APP_DIR, 'static'), filename)


@app.template_filter('datetimeformat')
def datetimeformat(value):
    try:
        dt = datetime.fromisoformat(value.replace('Z', '+00:00'))
        return dt.strftime('%b %d, %Y, %H:%M')
    except Exception:
        return value


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=True)
