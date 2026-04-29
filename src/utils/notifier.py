"""
notifier.py
NorthStar Property Management

Unified alert delivery: SMTP email + optional Twilio SMS.
All other modules call send_alert() — they don't care how it gets there.
"""

import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv
from pathlib import Path

# Load from .env at repo root
env_path = Path(__file__).parent.parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
SMTP_USER = os.getenv("SMTP_USER", "")
SMTP_PASS = os.getenv("SMTP_PASS", "")
ALERT_FROM = os.getenv("ALERT_FROM", SMTP_USER)
OWNER_EMAIL = os.getenv("OWNER_EMAIL", "")

TWILIO_SID = os.getenv("TWILIO_ACCOUNT_SID", "")
TWILIO_TOKEN = os.getenv("TWILIO_AUTH_TOKEN", "")
TWILIO_FROM = os.getenv("TWILIO_FROM_NUMBER", "")


def send_alert(
    subject: str,
    body: str,
    to: str = None,
    sms_to: str = None,
) -> None:
    """
    Send an alert email (and optionally SMS).
    Defaults to owner email if `to` is not specified.
    Logs to stdout — never silently fails.
    """
    recipient = to or OWNER_EMAIL
    if not recipient:
        print(f"[NOTIFIER] ⚠️  No recipient configured. Subject: {subject}")
        return

    _send_email(subject=subject, body=body, to=recipient)

    if sms_to and TWILIO_SID:
        _send_sms(body=f"{subject}\n\n{body[:120]}", to=sms_to)


def _send_email(subject: str, body: str, to: str) -> None:
    if not SMTP_USER or not SMTP_PASS:
        print(f"[NOTIFIER] ⚠️  SMTP not configured. Would send: {subject}")
        return

    try:
        msg = MIMEMultipart()
        msg["From"] = ALERT_FROM
        msg["To"] = to
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain"))

        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.ehlo()
            server.starttls()
            server.login(SMTP_USER, SMTP_PASS)
            server.sendmail(ALERT_FROM, to, msg.as_string())

        print(f"[NOTIFIER] ✅ Email sent → {to} | {subject}")
    except Exception as e:
        print(f"[NOTIFIER] ❌ Email failed: {e}")


def _send_sms(body: str, to: str) -> None:
    try:
        from twilio.rest import Client
        client = Client(TWILIO_SID, TWILIO_TOKEN)
        message = client.messages.create(body=body, from_=TWILIO_FROM, to=to)
        print(f"[NOTIFIER] ✅ SMS sent → {to} | SID: {message.sid}")
    except ImportError:
        print("[NOTIFIER] ⚠️  Twilio not installed. Run: pip install twilio")
    except Exception as e:
        print(f"[NOTIFIER] ❌ SMS failed: {e}")
