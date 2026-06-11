"""구조화된 데이터를 IB 리포트급 HTML로 렌더링 (GitHub Pages 풀페이지용)"""
import json
from datetime import datetime
import pytz


PAGE_TEMPLATE = """<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Daily Markets Brief — {date_short}</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Newsreader:opsz,wght@6..72,400;6..72,500;6..72,600;6..72,700&family=Inter:wght@400;500;600&family=IBM+Plex+Mono:wght@400;500;600&family=Noto+Sans+KR:wght@400;500;700&display=swap" rel="stylesheet">
<style>
  :root {{
    --ink: #1a1a18; --ink-soft: #44443f; --ink-mute: #6b6760; --ink-faint: #94918a;
    --paper: #faf9f5; --line: #e0ddd2; --line-soft: #ebe8df; --line-strong: #1a1a18;
    --accent: #00827F; --up: #1a6b3a; --down: #9a1f1f;
    --pri-bg: #f9e4e0; --pri-tx: #6a1818; --mac-bg: #dde8f3; --mac-tx: #0c3a64; --eq-bg: #dde9d2; --eq-tx: #234e0c;
  }}
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  html {{ -webkit-text-size-adjust: 100%; }}
  body {{ font-family: 'Inter','Noto Sans KR',-apple-system,sans-serif; color: var(--ink); background: #efece3; line-height: 1.55; padding: 28px 16px 60px; }}
  .sheet {{ max-width: 760px; margin: 0 auto; background: var(--paper); border: 1px solid var(--line); box-shadow: 0 1px 3px rgba(0,0,0,0.04),0 8px 24px rgba(0,0,0,0.06); }}
  .inner {{ padding: 44px 52px 40px; }}
  @media (max-width: 600px) {{ .inner {{ padding: 28px 22px 32px; }} body {{ padding: 12px 8px 40px; }} }}
  .topbar {{ display: flex; justify-content: space-between; align-items: center; font-family: 'IBM Plex Mono',monospace; font-size: 10px; letter-spacing: 0.14em; text-transform: uppercase; color: var(--ink-mute); padding-bottom: 16px; border-bottom: 3px double var(--line-strong); }}
  .topbar .brand {{ font-weight: 600; color: var(--ink); }}
  .masthead {{ padding: 22px 0 18px; border-bottom: 2px solid var(--line-strong); }}
  .mast-title {{ font-family: 'Newsreader',Georgia,serif; font-size: 46px; font-weight: 600; line-height: 0.98; letter-spacing: -0.02em; color: var(--ink); }}
  .mast-sub {{ font-family: 'IBM Plex Mono',monospace; font-size: 11px; color: var(--ink-mute); margin-top: 10px; letter-spacing: 0.04em; }}
  .mast-sub .live {{ color: var(--accent); font-weight: 600; }}
  .lead {{ font-family: 'Noto Sans KR',sans-serif; font-size: 14.5px; line-height: 1.85; color: var(--ink-soft); padding: 22px 0 20px; border-bottom: 1px solid var(--line); }}
  .strip {{ width: 100%; border-collapse: collapse; margin: 22px 0 6px; border-top: 1px solid var(--line-strong); border-bottom: 1px solid var(--line-strong); }}
  .strip td {{ padding: 12px 14px; border-right: 1px solid var(--line); width: 25%; vertical-align: top; }}
  .strip td:last-child {{ border-right: none; }}
  .strip-name {{ font-family: 'IBM Plex Mono',monospace; font-size: 9.5px; letter-spacing: 0.1em; text-transform: uppercase; color: var(--ink-mute); margin-bottom: 5px; }}
  .strip-val {{ font-family: 'IBM Plex Mono',monospace; font-size: 19px; font-weight: 600; color: var(--ink); letter-spacing: -0.01em; }}
  .strip-chg {{ font-family: 'IBM Plex Mono',monospace; font-size: 11px; font-weight: 500; margin-top: 3px; }}
  .up {{ color: var(--up); }} .down {{ color: var(--down); }} .flat {{ color: var(--ink-mute); }}
  @media (max-width: 600px) {{ .strip {{ display: grid; grid-template-columns: 1fr 1fr; }} .strip td {{ display: block; width: auto; border-bottom: 1px solid var(--line); }} .strip td:nth-child(even) {{ border-right: none; }} }}
  .sec {{ margin-top: 32px; }}
  .sec-head {{ display: flex; align-items: baseline; gap: 12px; padding-bottom: 7px; border-bottom: 2px solid var(--line-strong); margin-bottom: 4px; }}
  .sec-no {{ font-family: 'IBM Plex Mono',monospace; font-size: 11px; font-weight: 600; color: var(--accent); }}
  .sec-name {{ font-size: 11px; font-weight: 600; letter-spacing: 0.13em; text-transform: uppercase; color: var(--ink); flex: 1; }}
  .sec-tag {{ font-family: 'IBM Plex Mono',monospace; font-size: 9px; font-weight: 600; letter-spacing: 0.1em; text-transform: uppercase; padding: 3px 9px; border-radius: 3px; }}
  .t-pri {{ background: var(--pri-bg); color: var(--pri-tx); }} .t-mac {{ background: var(--mac-bg); color: var(--mac-tx); }} .t-eq {{ background: var(--eq-bg); color: var(--eq-tx); }}
  .item {{ padding: 16px 0; border-bottom: 1px solid var(--line-soft); }}
  .item:last-child {{ border-bottom: none; }}
  .meta {{ display: flex; flex-wrap: wrap; gap: 6px; align-items: center; margin-bottom: 7px; }}
  .src {{ font-family: 'IBM Plex Mono',monospace; font-size: 9.5px; font-weight: 600; letter-spacing: 0.08em; text-transform: uppercase; color: var(--ink-soft); }}
  .kw {{ font-family: 'IBM Plex Mono',monospace; font-size: 8.5px; font-weight: 600; letter-spacing: 0.06em; text-transform: uppercase; padding: 2px 6px; border-radius: 3px; }}
  .kw-kr {{ background: #d4eee0; color: #0f5d3e; }} .kw-mx {{ background: #f4e6cc; color: #6e3e08; }} .kw-auto {{ background: #e2dffa; color: #2e2774; }} .kw-gen {{ background: #eceae3; color: #5f5e5a; }}
  .head {{ font-family: 'Newsreader',Georgia,serif; font-size: 21px; font-weight: 600; line-height: 1.24; letter-spacing: -0.011em; color: var(--ink); margin-bottom: 7px; }}
  .item.sub .head {{ font-size: 17px; }}
  .lede {{ font-size: 13.5px; line-height: 1.68; color: var(--ink-soft); }}
  .lede-kr {{ font-family: 'Noto Sans KR',sans-serif; font-size: 13px; line-height: 1.78; }}
  .tk {{ font-family: 'IBM Plex Mono',monospace; font-size: 9px; font-weight: 500; padding: 2px 6px; background: #efece3; border: 1px solid var(--line); color: var(--ink-soft); border-radius: 3px; }}
  .tape-grp {{ margin-top: 14px; }}
  .tape-cat {{ font-family: 'IBM Plex Mono',monospace; font-size: 9.5px; font-weight: 600; letter-spacing: 0.12em; color: var(--accent); margin-bottom: 6px; padding-bottom: 3px; border-bottom: 1px solid var(--line-soft); }}
  .tape-row {{ display: flex; gap: 9px; padding: 5px 0; font-size: 13px; line-height: 1.5; color: var(--ink-soft); }}
  .tape-row .bull {{ color: var(--accent); font-family: 'IBM Plex Mono',monospace; font-weight: 600; flex-shrink: 0; }}
  .tape-row .tsrc {{ color: var(--ink-faint); font-size: 11px; }}
  .tape-badge {{ display: inline-block; font-family: 'IBM Plex Mono',monospace; font-size: 9px; font-weight: 600; letter-spacing: 0.1em; padding: 3px 9px; border-radius: 4px; margin-bottom: 8px; border: none; }}
  .tb-macro {{ background: #eef3f7; color: #3b5973; }}
  .tb-equities {{ background: #edf5ee; color: #2e5c3a; }}
  .tb-em {{ background: #fdf5ea; color: #735129; }}
  .tb-credit {{ background: #f3edf7; color: #5c2e61; }}
  .tb-commodities {{ background: #f7f0e8; color: #6e4a1f; }}
  .foot {{ margin-top: 34px; padding-top: 18px; border-top: 3px double var(--line-strong); font-family: 'IBM Plex Mono',monospace; font-size: 10px; line-height: 1.7; color: var(--ink-mute); }}
  .foot b {{ color: var(--ink-soft); font-weight: 600; }}
  .foot .disc {{ margin-top: 8px; font-style: italic; color: var(--ink-faint); }}
</style>
</head>
<body>
<div class="sheet">
  <div class="inner">
    <div class="topbar"><span class="brand">Daily Markets Brief</span><span>Mexico City Desk · Vol. {vol} · No. {issue}</span></div>
    <div class="masthead">
      <div class="mast-title">Morning Brief</div>
      <div class="mast-sub">{date_full} &nbsp;·&nbsp; Mexico City &nbsp;·&nbsp; {time_local} {tz_abbr} &nbsp;·&nbsp; <span class="live">LIVE</span></div>
    </div>
    <div class="lead">{lead}</div>
    <table class="strip"><tr>{strip_cells}</tr></table>
    <div class="sec"><div class="sec-head"><span class="sec-no">§ 01</span><span class="sec-name">Front of Book · Korea / Mexico / Auto</span><span class="sec-tag t-pri">Priority</span></div>{priority_html}</div>
    <div class="sec"><div class="sec-head"><span class="sec-no">§ 02</span><span class="sec-name">Macro &amp; Cross-Asset</span><span class="sec-tag t-mac">Macro</span></div>{macro_html}</div>
    <div class="sec"><div class="sec-head"><span class="sec-no">§ 03</span><span class="sec-name">Single-Name &amp; Corporate</span><span class="sec-tag t-eq">Equity</span></div>{single_html}</div>
    <div class="sec"><div class="sec-head"><span class="sec-no">§ 04</span><span class="sec-name">Also on the Tape · Filtered Headlines</span></div>{tape_html}</div>
    <div class="foot">
      <b>Sources</b> &nbsp;WSJ 10-Point · Markets A.M. · WSJ Politics · NYT · AP · El Financiero · Banxico<br>
      <b>Filters</b> &nbsp;Korea · Mexico · Automotive · USMCA · Fed · Banxico · EM · Tariff · KRW · MXN
      <div class="disc">Compiled automatically for internal reference. Not investment advice.</div>
    </div>
  </div>
</div>
</body>
</html>
"""


import re

USE_BADGE_STYLE = True

def _clean_source_suffix(text):
    if not text:
        return ""
    # 괄호형 출처 제거: "... (El Financiero)" / "... (translated)"
    text = re.sub(r"\s*\((?:[A-Za-z][A-Za-z.]*\s*){1,3}\)\s*$", "", text).strip()
    # 대시형 출처 제거: 대문자로 시작하는 매체명 1~4단어 ("WSJ", "WSJ / Market Data", "El Financiero")
    # 소문자로 시작하는 본문 끝맺음("— markets rally")은 보존
    text = re.sub(r"\s*[—–\-]{1,2}\s*(?:[A-Z][A-Za-z.]*(?:\s*/\s*|\s+)?){1,4}\s*$", "", text).strip()
    return text


def _kw(tag):
    cls = {"KR": "kw-kr", "MX": "kw-mx", "AUTO": "kw-auto"}.get(tag, "kw-gen")
    return f'<span class="kw {cls}">{tag}</span>'


def _priority(items):
    out = []
    for i, it in enumerate(items):
        kws = "".join(_kw(t) for t in it.get("tags", []))
        cls = "item" if i == 0 else "item sub"
        out.append(f'<div class="{cls}"><div class="meta"><span class="src">{it.get("source","")}</span>{kws}</div><div class="head">{it.get("headline","")}</div><div class="lede lede-kr">{it.get("lede","")}</div></div>')
    return "\n".join(out)


def _macro(items):
    return "\n".join(f'<div class="item"><div class="meta"><span class="src">{it.get("source","")}</span></div><div class="head">{it.get("headline","")}</div><div class="lede">{it.get("lede","")}</div></div>' for it in items)


def _single(items):
    out = []
    for it in items:
        tk = f'<span class="tk">{it["ticker"]}</span>' if it.get("ticker") else ""
        out.append(f'<div class="item"><div class="meta"><span class="src">{it.get("source","")}</span>{tk}</div><div class="head">{it.get("headline","")}</div><div class="lede">{it.get("lede","")}</div></div>')
    return "\n".join(out)


def _tape(items):
    by = {}
    for it in items:
        by.setdefault(it.get("category", "MACRO"), []).append(it)
    order = ["MACRO", "EQUITIES", "EM", "CREDIT", "COMMODITIES"]
    out = []
    for cat in order:
        if cat not in by:
            continue
        rows = []
        for it in by[cat]:
            clean = _clean_source_suffix(it["text"])
            src = f'<span class="tsrc">— {it.get("source","")}</span>' if it.get("source") else ""
            rows.append(f'<div class="tape-row"><span class="bull">›</span><span>{clean} {src}</span></div>')
        if USE_BADGE_STYLE:
            header = f'<div class="tape-badge tb-{cat.lower()}">{cat}</div>'
        else:
            header = f'<div class="tape-cat">{cat}</div>'
        out.append(f'<div class="tape-grp">{header}{"".join(rows)}</div>')
    return "\n".join(out)


def _strip(strip):
    cells = []
    for label, d in strip.items():
        chg, pct = d["change"], d["change_pct"]
        cls = "up" if chg > 0 else ("down" if chg < 0 else "flat")
        sign = "+" if chg >= 0 else ""
        is_y = "10Y" in label
        val = f"{d['price']:.3f}" if is_y else f"{d['price']:,.2f}"
        disp = f"{sign}{int(chg*100)} bps" if is_y else f"{sign}{chg:.2f} · {sign}{pct:.2f}%"
        cells.append(f'<td><div class="strip-name">{label}</div><div class="strip-val">{val}</div><div class="strip-chg {cls}">{disp}</div></td>')
    return "\n".join(cells)


def render(structured, market_strip, issue_number=1):
    tz = pytz.timezone("America/Mexico_City")
    now = datetime.now(tz)
    return PAGE_TEMPLATE.format(
        date_full=now.strftime("%A, %B %d, %Y"),
        date_short=now.strftime("%Y-%m-%d"),
        time_local=now.strftime("%H:%M"),
        tz_abbr=now.strftime("%Z"),
        vol=f"{now.year - 2025}",
        issue=f"{issue_number:03d}",
        lead=structured.get("lead_paragraph", ""),
        strip_cells=_strip(market_strip),
        priority_html=_priority(structured.get("priority_items", [])),
        macro_html=_macro(structured.get("macro_items", [])),
        single_html=_single(structured.get("single_name_items", [])),
        tape_html=_tape(structured.get("also_on_tape", [])),
    )
