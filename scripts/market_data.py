"""마켓 스트립용 시장 데이터 수집 (Yahoo Finance 무료 엔드포인트)"""
import requests


TICKERS = {
    "S&P 500 Fut": "ES=F",
    "USD/MXN": "MXN=X",
    "USD/KRW": "KRW=X",
    "UST 10Y": "^TNX",
}


def fetch_quote(symbol):
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}"
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        r = requests.get(url, headers=headers, timeout=10)
        r.raise_for_status()
        data = r.json()
        result = data["chart"]["result"][0]
        meta = result["meta"]
        price = meta.get("regularMarketPrice")
        prev = meta.get("chartPreviousClose") or meta.get("previousClose")
        if price is None or prev is None:
            return None
        change = price - prev
        change_pct = (change / prev) * 100 if prev else 0
        return {"price": price, "change": change, "change_pct": change_pct}
    except Exception as e:
        print(f"[WARN] quote fetch failed for {symbol}: {e}")
        return None


def fetch_market_strip():
    out = {}
    for label, sym in TICKERS.items():
        q = fetch_quote(sym)
        if q:
            out[label] = q
    return out


if __name__ == "__main__":
    res = fetch_market_strip()
    for k, v in res.items():
        print(f"{k}: {v['price']:.2f}  ({v['change']:+.2f}, {v['change_pct']:+.2f}%)")
