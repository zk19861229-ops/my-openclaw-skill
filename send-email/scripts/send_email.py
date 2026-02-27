#!/usr/bin/env python3
"""Send email via SMTP (163/126/QQ/Gmail etc.)"""

import argparse
import json
import smtplib
import sys
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from pathlib import Path


def send_email(
    smtp_host: str,
    smtp_port: int,
    username: str,
    password: str,
    to: list[str],
    subject: str,
    body: str,
    html: bool = False,
    cc: list[str] | None = None,
    bcc: list[str] | None = None,
    attachments: list[str] | None = None,
    reply_to: str | None = None,
    use_ssl: bool = True,
):
    msg = MIMEMultipart()
    msg["From"] = username
    msg["To"] = ", ".join(to)
    msg["Subject"] = subject

    if cc:
        msg["Cc"] = ", ".join(cc)
    if reply_to:
        msg["Reply-To"] = reply_to

    content_type = "html" if html else "plain"
    msg.attach(MIMEText(body, content_type, "utf-8"))

    if attachments:
        for filepath in attachments:
            p = Path(filepath)
            if not p.exists():
                print(f"WARNING: attachment not found: {filepath}", file=sys.stderr)
                continue
            part = MIMEBase("application", "octet-stream")
            part.set_payload(p.read_bytes())
            encoders.encode_base64(part)
            part.add_header("Content-Disposition", f'attachment; filename="{p.name}"')
            msg.attach(part)

    all_recipients = list(to)
    if cc:
        all_recipients.extend(cc)
    if bcc:
        all_recipients.extend(bcc)

    if use_ssl:
        server = smtplib.SMTP_SSL(smtp_host, smtp_port, timeout=30)
    else:
        server = smtplib.SMTP(smtp_host, smtp_port, timeout=30)
        server.starttls()

    try:
        server.login(username, password)
        server.sendmail(username, all_recipients, msg.as_string())
        print(json.dumps({"status": "ok", "to": all_recipients, "subject": subject}))
    finally:
        server.quit()


def main():
    parser = argparse.ArgumentParser(description="Send email via SMTP")
    parser.add_argument("--host", default="smtp.163.com", help="SMTP host")
    parser.add_argument("--port", type=int, default=465, help="SMTP port")
    parser.add_argument("--user", required=True, help="SMTP username/email")
    parser.add_argument("--pass", dest="password", required=True, help="SMTP password/auth code")
    parser.add_argument("--to", required=True, nargs="+", help="Recipient(s)")
    parser.add_argument("--subject", required=True, help="Email subject")
    parser.add_argument("--body", required=True, help="Email body text")
    parser.add_argument("--html", action="store_true", help="Send as HTML")
    parser.add_argument("--cc", nargs="*", help="CC recipient(s)")
    parser.add_argument("--bcc", nargs="*", help="BCC recipient(s)")
    parser.add_argument("--attach", nargs="*", help="Attachment file path(s)")
    parser.add_argument("--reply-to", help="Reply-To address")
    parser.add_argument("--no-ssl", action="store_true", help="Use STARTTLS instead of SSL")

    args = parser.parse_args()

    send_email(
        smtp_host=args.host,
        smtp_port=args.port,
        username=args.user,
        password=args.password,
        to=args.to,
        subject=args.subject,
        body=args.body,
        html=args.html,
        cc=args.cc,
        bcc=args.bcc,
        attachments=args.attach,
        reply_to=args.reply_to,
        use_ssl=not args.no_ssl,
    )


if __name__ == "__main__":
    main()
