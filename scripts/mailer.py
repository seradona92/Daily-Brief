"""브리핑 링크를 깔끔한 이메일로 발송"""
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime
import pytz

EMAIL_TEMPLATE = """<!DOCTYPE html>
<html><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0"></head>
<body style="margin:0;padding:0;background:#efece3;font-family:Georgia,'Times New Roman',serif;">
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background:#efece3;padding:32px 16px;">
<tr><td align="center">
<table role="presentation" width="460" cellpadding="0" cellspacing="0" style="max-width:460px;background:#faf9f5;border:1px solid #e0ddd2;">
<tr><td style="padding:40px 44px;">
  <div style="font-family:'Courier New',monospace;font-size:10px;letter-spacing:2px;text-transform:uppercase;color:#6b6760;padding-bottom:14px;border-bottom:3px double #1a1a18;">Daily Markets Brief &nbsp;·&nbsp; Mexico City Desk</div>
  <div style="font-size:34px;font-weight:bold;color:#1a1a18;letter-spacing:-1px;padding:22px 0 6px;">Morning Brief</div>
  <div style="font-family:'Courier New',monospace;font-size:12px;color:#6b6760;padding-bottom:24px;">{date_full}</div>
  <div style="font-family:Arial,sans-serif;font-size:14px;line-height:1.7;color:#44443f;padding-bottom:28px;">오늘의 브리핑이 준비되었습니다. 아래 버튼을 눌러 전체 리포트를 확인하세요.</div>
  <table role="presentation" cellpadding="0" cellspacing="0"><tr><td style="background:#1a1a18;border-radius:4px;">
    <a href="{page_url}" style="display:inline-block;padding:14px 32px;font-family:Arial,sans-serif;font-size:14px;font-weight:bold;color:#faf9f5;text-decoration:none;letter-spacing:0.5px;">오늘 브리핑 열기 →</a>
  </td></tr></table>
  <div style="font-family:Arial,sans-serif;font-size:12px;line-height:1.6;color:#94918a;padding-top:28px;margin-top:24px;border-top:1px solid #ebe8df;">
    <a href="{archive_url}" style="color:#00827F;text-decoration:none;">지난 브리핑 보기 (Archive)</a><br>
    <span style="font-style:italic;">Internal reference only. Not investment advice.</span>
  </div>
</td></tr>
</table>
</td></tr>
</table>
</body></html>
"""


def send_brief(page_url, date_str=None):
    sender = os.environ["GMAIL_SENDER"]
    recipient = os.environ["GMAIL_RECIPIENT"]
    password = os.environ["GMAIL_APP_PASSWORD"]

    tz = pytz.timezone("America/Mexico_City")
    now = datetime.now(tz)
    date_full = now.strftime("%A, %B %d, %Y")
    subject = f"Daily Markets Brief — {now.strftime('%Y-%m-%d (%a)')}"

    archive_url = page_url.rsplit("/", 1)[0] + "/"

    body = EMAIL_TEMPLATE.format(date_full=date_full, page_url=page_url, archive_url=archive_url)

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = f"Daily Brief <{sender}>"
    msg["To"] = recipient
    msg.attach(MIMEText(f"오늘의 브리핑: {page_url}", "plain", "utf-8"))
    msg.attach(MIMEText(body, "html", "utf-8"))

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(sender, password)
        server.send_message(msg)
    print(f"[OK] Brief link sent to {recipient}")


if __name__ == "__main__":
    send_brief("https://seradona92.github.io/Daily-Brief/latest.html")
