"""구조화된 데이터를 IB 모닝노트 HTML로 렌더링"""
import json
from datetime import datetime
import pytz


TEMPLATE = """<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<title>Daily Markets Brief — {date_short}</title>
<style>
  @import url('https://fonts.googleapis.com/css2?family=Source+Serif+Pro:wght@400;500;600&family=Inter:wght@400;500&family=JetBrains+Mono:wght@400;500&display=swap');
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{ font-family: 'Inter', -apple-system, sans-serif; color: #1a1a1a; background: #f5f3ee; padding: 32px 16px; line-height: 1.5; }}
  .wrap {{ max-width: 720px; margin: 0 auto; background: #fdfcf8; padding: 36px 44px; border: 0.5px solid #d8d4c8; }}
  .masthead {{ border-bottom: 2px solid #1a1a1a; padding-bottom: 14px; margin-bottom: 22px; }}
  .mast-top {{ display: flex; justify-content: space-between; font-size: 10px; letter-spacing: 0.14em; text-transform: uppercase; color: #6b6760; margin-bottom: 8px; font-weight: 500; }}
  .mast-title {{ font-family: 'Source Serif Pro', Georgia, serif; font-size: 32px; font-weight: 500; line-height: 1; letter-spacing: -0.01em; }}
  .mast-sub {{ font-size: 12px; color: #6b6760; margin-top: 6px; font-style: italic; }}
  .lead {{ font-family: 'Source Serif Pro', serif; font-size: 14px; line-height: 1.7; padding: 14px 0; border-bottom: 0.5px solid #d8d4c8; margin-bottom: 4px; color: #2a2a2a; }}
  .lead::first-letter {{ font-size: 28px; font-weight: 600; float: left; line-height: 0.9; padding: 3px 6px 0 0; }}
  .strip {{ width: 100%; border-collapse: collapse; border: 1px solid #c4bfb0; margin: 16px 0 8px; }}
  .strip td {{ padding: 8px 10px; border-right: 1px solid #c4bfb0; width: 25%; vertical-align: top; }}
  .strip td:last-child {{ border-right: none; }}
  .strip-name {{ font-size: 9px; letter-spacing: 0.08em; text-transform: uppercase; color: #6b6760; margin-bottom: 3px; font-weight: 500; }}
  .strip-val {{ font-family: 'JetBrains Mono', monospace; font-size: 14px; font-weight: 500; }}
  .strip-chg {{ font-family: 'JetBrains Mono', monospace; font-size: 10px; margin-top: 2px; }}
  .up {{ color: #1a6b3a; }}
  .down {{ color: #9a1f1f; }}
  .flat {{ color: #6b6760; }}
  .sec {{ margin-top: 24px; }}
  .sec-bar {{ display: flex; align-items: baseline; gap: 12px; padding-bottom: 6px; border-bottom: 1px solid #1a1a1a; margin-bottom: 10px; }}
  .sec-num {{ font-family: 'JetBrains Mono', monospace; font-size: 10px; color: #6b6760; }}
  .sec-label {{ font-size: 10px; letter-spacing: 0.12em; text-transform: uppercase; font-weight: 500; flex: 1; }}
  .sec-tag {{ font-size: 9px; letter-spacing: 0.08em; text-transform: uppercase; padding: 2px 7px; }}
  .tag-pri {{ background: #f3dada; color: #6a1818; }}
  .tag-mac {{ background: #dde8f3; color: #0c3a64; }}
  .tag-eq {{ background: #dde9d2; color: #234e0c; }}
  .item {{ padding: 12px 0; border-bottom: 0.5px solid #e5e2d8; }}
  .item:last-child {{ border-bottom: none; }}
  .item-meta {{ display: flex; gap: 8px; align-items: center; font-size: 9px; letter-spacing: 0.06em; text-transform: uppercase; color: #6b6760; margin-bottom: 4px; }}
  .item-source {{ font-weight: 500; color: #1a1a1a; }}
  .item-head {{ font-family: 'Source Serif Pro', serif; font-size: 17px; font-weight: 500; line-height: 1.3; margin-bottom: 5px; letter-spacing: -0.005em; }}
  .item-lede {{ font-size: 13px; line-height: 1.6; color: #3a3a3a; }}
  .pill {{ display: inline-block; font-family: 'JetBrains Mono', monospace; font-size: 9px; padding: 1px 6px; margin-left: 4px; font-weight: 500; }}
  .p-kr {{ background: #d4eee0; color: #0f5d3e; }}
  .p-mx {{ background: #f4e6cc; color: #6e3e08; }}
  .p-auto {{ background: #e2dffa; color: #2e2774; }}
  .p-fed {{ background: #f3e0e0; color: #6a1818; }}
  .ticker {{ font-family: 'JetBrains Mono', monospace; font-size: 9px; padding: 1px 5px; background: #ebe8df; color: #1a1a1a; margin-left: 4px; }}
  .tape-group {{ margin-top: 10px; }}
  .tape-cat {{ font-family: 'JetBrains Mono', monospace; font-size: 9px; letter-spacing: 0.08em; color: #6b6760; margin-bottom: 4px; }}
  .tape-row {{ display: flex; gap: 8px; padding: 4px 0; font-size: 12px; line-height: 1.5; }}
  .tape-bullet {{ color: #6b6760; font-family: 'JetBrains Mono', monospace; font-size: 10px; padding-top: 3px; min-width: 12px; }}
  .tape-src {{ color: #8a8780; font-size: 11px; margin-left: 6px; }}
  .footer {{ margin-top: 28px; padding: 12px 14px; background: #ebe8df; font-size: 10px; color: #6b6760; line-height: 1.55; border-left: 2px solid #c4bfb0; }}
  .footer strong {{ color: #1a1a1a; font-weight: 500; }}
</style>
</head>
<body>
<div class="wrap">
  <div class="masthead">
    <div class="mast-top">
      <span>Daily Markets Brief · Mexico City Desk</span>
      <span>Vol. {vol} · No. {issue}</span>
    </div>
    <div class="mast-title">Morning Brief</div>
    <div class="mast-sub">{date_full} · {city} · {time_local} {tz_abbr}</div>
  </div>

  <div class="lead">{lead}</div>

  <table class="strip"><tr>{strip_cells}</tr></table>

  <div class="sec">
    <div class="sec-bar">
      <span class="sec-num">§ 01</span>
      <span class="sec-label">Front of Book · Korea / Mexico / Auto</span>
      <span class="sec-tag tag-pri">Priority</span>
    </div>
    {priority_html}
  </div>

  <div class="sec">
    <div class="sec-bar">
      <span class="sec-num">§ 02</span>
      <span class="sec-label">Macro & Cross-Asset</span>
      <span class="sec-tag tag-mac">Macro</span>
    </div>
    {macro_html}
  </div>

  <div class="sec">
    <div class="sec-bar">
      <span class="sec-num">§ 03</span>
      <span class="sec-label">Single-Name & Corporate</span>
      <span class="sec-tag tag-eq">Equity</span>
    </div>
    {single_html}
  </div>

  <div class="sec">
    <div class="sec-bar">
      <span class="sec-num">§ 04</span>
      <span class="sec-label">Also on the Tape · Filtered Headlines</span>
    </div>
    {tape_html}
  </div>

  <div class="footer">
    <strong>Sources:</strong> WSJ 10-Point, Markets A.M., WSJ Politics, Reuters, NYT, Yonhap, El Financiero, Banxico.<br>
    <strong>Filters applied:</strong> Korea · Mexico · Automotive · USMCA · Fed · Banxico · EM · Tariff · KRW · MXN.<br>
    Internal reference only. Not investment advice.
  </div>
</div>
</body>
</html>
"""


def _pill(tag):
    classes = {"KR": "p-kr", "MX": "p-mx", "AUTO": "p-auto", "FED": "p-fed"}
    return f'<span class="pill {classes.get(tag, "p-kr")}">{tag}</span>'


def _render_priority(items):
    out = []
    for it in items:
        tags_html = "".join(_pill(t) for t in it.get("tags", []))
        out.append(f'''
        <div class="item">
          <div class="item-meta">
            <span class="item-source">{it.get("source", "")}</span>
            {tags_html}
          </div>
          <div class="item-head">{it.get("headline", "")}</div>
          <div class="item-lede">{it.get("lede", "")}</div>
        </div>''')
    return "\n".join(out)


def _render_macro(items):
    out = []
    for it in items:
        out.append(f'''
        <div class="item">
          <div class="item-meta"><span class="item-source">{it.get("source", "")}</span></div>
          <div class="item-head">{it.get("headline", "")}</div>
          <div class="item-lede">{it.get("lede", "")}</div>
        </div>''')
    return "\n".join(out)


def _render_single(items):
    out = []
    for it in items:
        ticker_html = f'<span class="ticker">{it["ticker"]}</span>' if it.get("ticker") else ""
        out.append(f'''
        <div class="item">
          <div class="item-meta">
            <span class="item-source">{it.get("source", "")}</span>
            {ticker_html}
          </div>
          <div class="item-head">{it.get("headline", "")}</div>
          <div class="item-lede">{it.get("lede", "")}</div>
        </div>''')
    return "\n".join(out)


def _render_tape(items):
    by_cat = {}
    for it in items:
        cat = it.get("category", "MACRO")
        by_cat.setdefault(cat, []).append(it)

    order = ["MACRO", "EQUITIES", "EM", "CREDIT", "COMMODITIES"]
    out = []
    for cat in order:
        if cat not in by_cat:
            continue
        rows = []
        for it in by_cat[cat]:
            src = f'<span class="tape-src">— {it.get("source", "")}</span>' if it.get("source") else ""
            rows.append(f'<div class="tape-row"><span class="tape-bullet">›</span><span>{it["text"]}{src}</span></div>')
        out.append(f'<div class="tape-group"><div class="tape-cat">{cat}</div>{"".join(rows)}</div>')
    return "\n".join(out)


def _render_strip(strip):
    cells = []
    for label, data in strip.items():
        chg = data["change"]
        pct = data["change_pct"]
        cls = "up" if chg > 0 else ("down" if chg < 0 else "flat")
        sign = "+" if chg >= 0 else ""
        is_yield = "10Y" in label
        val_fmt = f"{data['price']:.3f}" if is_yield else f"{data['price']:,.2f}"
        chg_fmt = f"{sign}{chg:.3f}" if is_yield else f"{sign}{chg:.2f}"
        unit = "bps" if is_yield else "%"
        if is_yield:
            chg_display = f"{sign}{int(chg*100)} {unit}"
        else:
            chg_display = f"{chg_fmt} · {sign}{pct:.2f}{unit}"
        cells.append(f'''<td>
          <div class="strip-name">{label}</div>
          <div class="strip-val">{val_fmt}</div>
          <div class="strip-chg {cls}">{chg_display}</div>
        </td>''')
    return "\n".join(cells)


def render(structured, market_strip, issue_number=1):
    tz = pytz.timezone("America/Mexico_City")
    now = datetime.now(tz)
    date_full = now.strftime("%A, %B %d, %Y")
    date_short = now.strftime("%Y-%m-%d")
    time_local = now.strftime("%H:%M")
    tz_abbr = now.strftime("%Z")

    vol = now.year - 2025
    issue = issue_number

    html = TEMPLATE.format(
        date_full=date_full,
        date_short=date_short,
        city="Mexico City",
        time_local=time_local,
        tz_abbr=tz_abbr,
        vol=f"{vol:01d}",
        issue=f"{issue:03d}",
        lead=structured.get("lead_paragraph", ""),
        strip_cells=_render_strip(market_strip),
        priority_html=_render_priority(structured.get("priority_items", [])),
        macro_html=_render_macro(structured.get("macro_items", [])),
        single_html=_render_single(structured.get("single_name_items", [])),
        tape_html=_render_tape(structured.get("also_on_tape", [])),
    )
    return html


if __name__ == "__main__":
    sample = {
        "lead_paragraph": "테스트 리드 문단입니다.",
        "priority_items": [{"headline": "테스트", "lede": "테스트 리드", "source": "Reuters", "tags": ["KR","MX"]}],
        "macro_items": [],
        "single_name_items": [],
        "also_on_tape": [],
    }
    strip = {"S&P 500 Fut": {"price": 7336.25, "change": 57.75, "change_pct": 0.79}}
    print(render(sample, strip)[:1000])
