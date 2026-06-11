"""docs/ 폴더에 브리핑 페이지 저장 + 아카이브 인덱스 생성 (GitHub Pages)"""
import os
import re
import glob
from datetime import datetime

DOCS = "docs"
REPO_USER = "seradona92"
REPO_NAME = "Daily-Brief"
BASE_URL = f"https://{REPO_USER}.github.io/{REPO_NAME}"

INDEX_TEMPLATE = """<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Daily Markets Brief — Archive</title>
<link href="https://fonts.googleapis.com/css2?family=Newsreader:opsz,wght@6..72,400;6..72,600&family=Inter:wght@400;500;600&family=IBM+Plex+Mono:wght@400;500&display=swap" rel="stylesheet">
<style>
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{ font-family: 'Inter',sans-serif; background: #efece3; color: #1a1a18; padding: 32px 16px 60px; line-height: 1.5; }}
  .wrap {{ max-width: 600px; margin: 0 auto; background: #faf9f5; border: 1px solid #e0ddd2; padding: 44px 48px; box-shadow: 0 8px 24px rgba(0,0,0,0.06); }}
  .top {{ font-family: 'IBM Plex Mono',monospace; font-size: 10px; letter-spacing: 0.14em; text-transform: uppercase; color: #6b6760; padding-bottom: 14px; border-bottom: 3px double #1a1a18; }}
  h1 {{ font-family: 'Newsreader',serif; font-size: 38px; font-weight: 600; letter-spacing: -0.02em; margin: 20px 0 4px; }}
  .sub {{ font-family: 'IBM Plex Mono',monospace; font-size: 11px; color: #6b6760; margin-bottom: 24px; }}
  .row {{ display: flex; align-items: baseline; justify-content: space-between; padding: 14px 0; border-bottom: 1px solid #ebe8df; text-decoration: none; color: inherit; transition: padding-left 0.12s; }}
  .row:hover {{ padding-left: 6px; }}
  .row .date {{ font-family: 'Newsreader',serif; font-size: 18px; font-weight: 600; }}
  .row .day {{ font-family: 'IBM Plex Mono',monospace; font-size: 11px; color: #94918a; }}
  .row .arrow {{ font-family: 'IBM Plex Mono',monospace; color: #00827F; }}
  .latest {{ background: #f9e4e0; color: #6a1818; font-family: 'IBM Plex Mono',monospace; font-size: 8.5px; font-weight: 600; letter-spacing: 0.08em; text-transform: uppercase; padding: 2px 7px; border-radius: 3px; margin-left: 8px; }}
</style>
</head>
<body>
<div class="wrap">
  <div class="top">Daily Markets Brief · Mexico City Desk</div>
  <h1>Archive</h1>
  <div class="sub">Updated {updated}</div>
  {rows}
</div>
</body>
</html>
"""


def _day_name(date_str):
    d = datetime.strptime(date_str, "%Y-%m-%d")
    return d.strftime("%A")


def write_brief_and_index(html, date_str):
    os.makedirs(DOCS, exist_ok=True)

    # .nojekyll so GitHub Pages serves as-is
    open(os.path.join(DOCS, ".nojekyll"), "w").close()

    page_name = f"{date_str}.html"
    with open(os.path.join(DOCS, page_name), "w", encoding="utf-8") as f:
        f.write(html)

    # latest.html = today (stable URL)
    with open(os.path.join(DOCS, "latest.html"), "w", encoding="utf-8") as f:
        f.write(html)

    # collect all dated pages
    pages = []
    for p in glob.glob(os.path.join(DOCS, "20*.html")):
        name = os.path.basename(p).replace(".html", "")
        if re.match(r"\d{4}-\d{2}-\d{2}", name):
            pages.append(name)
    pages = sorted(set(pages), reverse=True)

    rows = []
    for i, ds in enumerate(pages):
        latest = '<span class="latest">Latest</span>' if i == 0 else ""
        rows.append(
            f'<a class="row" href="{ds}.html"><span><span class="date">{ds}</span>{latest}</span>'
            f'<span class="day">{_day_name(ds)} <span class="arrow">→</span></span></a>'
        )

    index_html = INDEX_TEMPLATE.format(
        updated=datetime.now().strftime("%Y-%m-%d %H:%M UTC"),
        rows="\n".join(rows),
    )
    with open(os.path.join(DOCS, "index.html"), "w", encoding="utf-8") as f:
        f.write(index_html)

    return f"{BASE_URL}/{page_name}"
