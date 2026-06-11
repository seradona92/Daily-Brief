"""완성된 HTML 브리핑을 이메일로 발송"""
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime
import pytz


def send_brief(html_content, subject=None):
    sender = os.environ["GMAIL_SENDER"]
    recipient = os.environ["GMAIL_RECIPIENT"]
    password = os.environ["GMAIL_APP_PASSWORD"]

    tz = pytz.timezone("America/Mexico_City")
    now = datetime.now(tz)
    if not subject:
        subject = f"Daily Markets Brief — {now.strftime('%Y-%m-%d (%a)')}"

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = f"Daily Brief <{sender}>"
    msg["To"] = recipient

    msg.attach(MIMEText(html_content, "html", "utf-8"))

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(sender, password)
        server.send_message(msg)

    print(f"[OK] Brief sent to {recipient}")


if __name__ == "__main__":
    send_brief("<html><body><h1>Test</h1></body></html>", subject="Test")
