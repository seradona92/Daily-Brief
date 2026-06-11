"""WSJ 뉴스레터 이메일 수집"""
import base64
import json
import os
from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime

from bs4 import BeautifulSoup
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build


SENDERS = {
    "10-point": "access@interactive.wsj.com",
    "markets-am": "access@interactive.wsj.com",
    "politics": "access@interactive.wsj.com",
    "intelligent-investor": "access@interactive.wsj.com",
}

SUBJECT_KEYWORDS = {
    "10-point": ["The 10-Point"],
    "markets-am": ["Markets A.M."],
    "politics": ["WSJ Politics"],
    "intelligent-investor": ["Intelligent Investor"],
}


def build_gmail_service():
    token_json = os.environ.get("GMAIL_TOKEN")
    if not token_json:
        raise RuntimeError("GMAIL_TOKEN env var missing")
    creds_info = json.loads(token_json)
    creds = Credentials.from_authorized_user_info(creds_info, ["https://www.googleapis.com/auth/gmail.readonly"])
    return build("gmail", "v1", credentials=creds, cache_discovery=False)


def _get_body_text(msg_payload):
    if "parts" in msg_payload:
        for part in msg_payload["parts"]:
            mime = part.get("mimeType", "")
            if mime == "text/html":
                data = part.get("body", {}).get("data")
                if data:
                    html = base64.urlsafe_b64decode(data).decode("utf-8", errors="ignore")
                    soup = BeautifulSoup(html, "lxml")
                    for tag in soup(["script", "style"]):
                        tag.decompose()
                    return soup.get_text(separator="\n", strip=True)
            if mime.startswith("multipart"):
                text = _get_body_text(part)
                if text:
                    return text
        for part in msg_payload["parts"]:
            if part.get("mimeType") == "text/plain":
                data = part.get("body", {}).get("data")
                if data:
                    return base64.urlsafe_b64decode(data).decode("utf-8", errors="ignore")
    body = msg_payload.get("body", {}).get("data")
    if body:
        return base64.urlsafe_b64decode(body).decode("utf-8", errors="ignore")
    return ""


def _header(headers, name):
    for h in headers:
        if h["name"].lower() == name.lower():
            return h["value"]
    return ""


def fetch_recent_newsletters(hours_back=24):
    service = build_gmail_service()
    cutoff = datetime.now(timezone.utc) - timedelta(hours=hours_back)
    query = f"from:({SENDERS['10-point']}) newer_than:2d"
    results = service.users().messages().list(userId="me", q=query, maxResults=20).execute()
    messages = results.get("messages", [])

    collected = {}
    for m in messages:
        msg = service.users().messages().get(userId="me", id=m["id"], format="full").execute()
        payload = msg["payload"]
        headers = payload.get("headers", [])
        subject = _header(headers, "Subject")
        date_str = _header(headers, "Date")
        try:
            sent_at = parsedate_to_datetime(date_str)
        except Exception:
            continue
        if sent_at < cutoff:
            continue

        for key, kws in SUBJECT_KEYWORDS.items():
            if any(kw.lower() in subject.lower() for kw in kws):
                if key in collected:
                    continue
                body = _get_body_text(payload)
                collected[key] = {
                    "subject": subject,
                    "sent_at": sent_at.isoformat(),
                    "body": body[:15000],
                }
                break
    return collected


if __name__ == "__main__":
    out = fetch_recent_newsletters()
    for k, v in out.items():
        print(f"\n=== {k} ===")
        print(f"Subject: {v['subject']}")
        print(f"Date: {v['sent_at']}")
        print(f"Body length: {len(v['body'])}")
