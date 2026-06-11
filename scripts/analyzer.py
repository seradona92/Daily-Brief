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
- priority_items: Lead with the 1-2 most globally significant stories today (regardless of Korea/Mexico angle) — choose what a Goldman Sachs analyst would front-page. Then add 1-2 Korea/Mexico/Auto specific items. MAX 1 Yonhap item per section.
- macro_items: 2-3 items on Fed/ECB/rates/FX/commodities. MAX 1 Yonhap.
- single_name_items: 2-3 items. MAX 1 Yonhap. Prefer companies with direct relevance to Korean auto supply chain or Mexican manufacturing.
- also_on_tape: 8-15 one-line English headlines, grouped by category. Include broad market news, not just Korea/Mexico.
- Section 1 main item: The single most important story a Korea-based credit analyst covering Mexico would need to know TODAY — could be geopolitical, macro, or sector-specific.
- Section 1 main item MUST be the single most market-moving or geopolitically significant story of the day — not just a Korea/Mexico story. Choose the story a Goldman Sachs analyst would lead with.
- Yonhap: MAX 1 item per section (§01, §02, §03 each).


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
        model="claude-sonnet-4-6",
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
