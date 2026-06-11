"""Claude API를 사용해 수집된 자료를 IB 모닝노트 구조로 변환"""
import json
import os
from anthropic import Anthropic


SYSTEM_PROMPT = """You are a senior credit analyst at a Korean bank in Mexico, drafting a daily IB-style morning markets brief for internal reference. Your readers are credit officers handling Korean corporate borrowers operating in Mexico (mostly automotive parts manufacturers).

Output language rules:
- lead_paragraph: KOREAN only — this is the day's macro context summary for a Korean reader
- priority_items headline: ENGLISH original (or translate Spanish sources to English)
- priority_items lede: KOREAN — 2-3 sentences with specific numbers/names
- macro_items headline: ENGLISH original
- macro_items lede: ENGLISH — concise, IB register
- single_name_items headline: ENGLISH original with ticker if available
- single_name_items lede: ENGLISH — facts only, no fluff
- also_on_tape text: ENGLISH one-liners (translate Spanish sources)
- Spanish sources (El Financiero, Banxico): translate headlines/ledes to English

Tone: Concise, factual, IB analyst register. No hype, no emoji, no marketing language.

Your task: From the raw inputs below, build a structured JSON output with sections.

Priority keywords (front-of-book): Korea, Korean, 한국, Mexico, Mexican, 멕시코, Hyundai, Kia, Samsung, LG, POSCO, Hanwha, automotive, auto parts, OEM, Tier-1, USMCA, tariff, 관세, KRW, MXN, peso, Banxico, nearshoring, AMLO, Sheinbaum, Yoon, Lee Jae-myung.

Required output format (strict JSON):
{
  "lead_paragraph": "한국어 2-3문장. 오늘의 핵심 매크로/마켓 스레드를 멕시코 내 한국계 여신 담당자 시각으로.",
  "priority_items": [
    {"headline": "English headline", "lede": "한국어 리드 2-3문장, 구체적 수치/인명 포함", "source": "WSJ/Reuters/Yonhap/etc", "tags": ["KR","MX","AUTO"]}
  ],
  "macro_items": [
    {"headline": "English headline", "lede": "English lede 2-3 sentences", "source": "..."}
  ],
  "single_name_items": [
    {"headline": "English headline", "lede": "English lede 1-2 sentences", "source": "...", "ticker": "optional"}
  ],
  "also_on_tape": [
    {"category": "MACRO|EQUITIES|EM|CREDIT|COMMODITIES", "text": "English one-liner", "source": "..."}
  ]
}

Rules:
- priority_items: 1 main item with full Korean lede + 2-3 short sub items
- macro_items: 2-3 items on Fed/ECB/rates/FX/commodities
- single_name_items: 2-3 items on specific companies (earnings, M&A, IPO, ratings)
- also_on_tape: 8-15 one-line English headlines, grouped by category
- Numbers must be specific (use exact figures from sources)
- Never invent data. If unsure, omit.
"""


def analyze_and_structure(emails, rss_items, market_strip):
    client = Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

    inputs_text = "## WSJ NEWSLETTERS\n"
    for key, data in emails.items():
        inputs_text += f"\n### {key.upper()}\nSubject: {data['subject']}\n{data['body'][:8000]}\n"

    inputs_text += "\n\n## RSS HEADLINES\n"
    for source, items in rss_items.items():
        inputs_text += f"\n### {source}\n"
        for it in items[:15]:
            inputs_text += f"- {it['title']}\n  {it.get('summary', '')[:300]}\n"

    inputs_text += "\n\n## MARKET DATA\n"
    for k, v in market_strip.items():
        inputs_text += f"- {k}: {v['price']:.2f} ({v['change']:+.2f}, {v['change_pct']:+.2f}%)\n"

    msg = client.messages.create(
        model="claude-opus-4-8",
        max_tokens=8000,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": f"Build the morning brief JSON from these inputs:\n\n{inputs_text}\n\nReturn ONLY valid JSON, no markdown fences."}],
    )

    text = msg.content[0].text.strip()
    if text.startswith("```"):
        text = text.split("```")[1]
        if text.startswith("json"):
            text = text[4:]
        text = text.strip()

    return json.loads(text)


if __name__ == "__main__":
    from email_fetcher import fetch_recent_newsletters
    from rss_fetcher import fetch_all_feeds
    from market_data import fetch_market_strip

    emails = fetch_recent_newsletters()
    rss = fetch_all_feeds()
    mkt = fetch_market_strip()
    result = analyze_and_structure(emails, rss, mkt)
    print(json.dumps(result, ensure_ascii=False, indent=2))
