# Daily Markets Brief

자동화된 IB 모닝노트 브리핑.

## 구조

```
.github/workflows/daily.yml   # GitHub Actions (매일 07:00 멕시코시티)
scripts/
  main.py                     # 메인 오케스트레이터
  email_fetcher.py            # WSJ 뉴스레터 수집
  rss_fetcher.py              # RSS 수집 (Reuters/NYT/Yonhap/El Financiero/Banxico)
  market_data.py              # 시장 데이터 (Yahoo Finance)
  analyzer.py                 # Claude API 분석
  renderer.py                 # IB HTML 렌더링
  mailer.py                   # SMTP 발송
requirements.txt
```

## 수동 실행
GitHub repo → Actions 탭 → Daily Brief → Run workflow

## 로컬 테스트
```
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
export ANTHROPIC_API_KEY=...
export GMAIL_SENDER=...
# ... 환경 변수 설정
python scripts/main.py
```
