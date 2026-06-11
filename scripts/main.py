"""메인 파이프라인: 수집 → 분석 → 렌더 → 발송"""
import json
import os
import sys
import traceback
from datetime import datetime
import pytz

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from email_fetcher import fetch_recent_newsletters
from rss_fetcher import fetch_all_feeds
from market_data import fetch_market_strip
from analyzer import analyze_and_structure
from renderer import render
from mailer import send_brief


def issue_number():
    tz = pytz.timezone("America/Mexico_City")
    now = datetime.now(tz)
    return now.timetuple().tm_yday


def main():
    print("[1/5] Fetching WSJ newsletters from Gmail...")
    try:
        emails = fetch_recent_newsletters(hours_back=30)
        print(f"      Got {len(emails)} newsletters: {list(emails.keys())}")
    except Exception as e:
        print(f"      WARN: Gmail fetch failed: {e}")
        emails = {}

    print("[2/5] Fetching RSS feeds...")
    try:
        rss = fetch_all_feeds(hours_back=24)
        print(f"      Got {len(rss)} feeds, total {sum(len(v) for v in rss.values())} items")
    except Exception as e:
        print(f"      WARN: RSS fetch partial: {e}")
        rss = {}

    print("[3/5] Fetching market data...")
    try:
        mkt = fetch_market_strip()
        print(f"      Got {len(mkt)} quotes")
    except Exception as e:
        print(f"      WARN: market data failed: {e}")
        mkt = {}

    if not emails and not rss:
        print("ERROR: No content collected. Aborting.")
        sys.exit(1)

    print("[4/5] Calling Claude API for structured analysis...")
    structured = analyze_and_structure(emails, rss, mkt)
    print(f"      Got {len(structured.get('priority_items', []))} priority items, "
          f"{len(structured.get('macro_items', []))} macro items, "
          f"{len(structured.get('also_on_tape', []))} tape items")

    print("[5/5] Rendering HTML and sending email...")
    html = render(structured, mkt, issue_number=issue_number())

    os.makedirs("output", exist_ok=True)
    out_path = f"output/brief_{datetime.now(pytz.timezone('America/Mexico_City')).strftime('%Y%m%d')}.html"
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"      Saved to {out_path}")

    send_brief(html)
    print("DONE.")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"FATAL: {e}")
        traceback.print_exc()
        sys.exit(1)
