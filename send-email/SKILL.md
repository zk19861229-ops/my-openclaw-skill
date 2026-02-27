---
name: send-email
description: Send emails via SMTP. Use when user asks to send email, compose email, mail someone, send notification, send report by email, or any email-related task. Supports plain text, HTML, attachments, CC/BCC, and batch sending.
---

# Send Email

Send emails via SMTP using `scripts/send_email.py`.

## Configuration

Default SMTP config (163 mailbox):
- Host: `smtp.163.com`
- Port: `465` (SSL)
- User: read from TOOLS.md or ask user

Credentials are stored in the workspace `TOOLS.md` under `### Email`.

## Usage

```bash
python scripts/send_email.py \
  --user "sender@163.com" \
  --pass "AUTH_CODE" \
  --to recipient@example.com \
  --subject "Subject" \
  --body "Email body"
```

### Options

| Flag | Description |
|------|-------------|
| `--host` | SMTP host (default: smtp.163.com) |
| `--port` | SMTP port (default: 465) |
| `--user` | Sender email (required) |
| `--pass` | Auth code (required) |
| `--to` | Recipient(s), space-separated (required) |
| `--subject` | Subject line (required) |
| `--body` | Body text (required) |
| `--html` | Treat body as HTML |
| `--cc` | CC recipient(s) |
| `--bcc` | BCC recipient(s) |
| `--attach` | File path(s) to attach |
| `--reply-to` | Reply-To address |
| `--no-ssl` | Use STARTTLS instead of SSL |

### Common SMTP Hosts

| Provider | Host | SSL Port |
|----------|------|----------|
| 163 | smtp.163.com | 465 |
| 126 | smtp.126.com | 465 |
| QQ | smtp.qq.com | 465 |
| Gmail | smtp.gmail.com | 465 |
| Outlook | smtp.office365.com | 587 (STARTTLS, use --no-ssl) |

## Workflow

1. Read email credentials from TOOLS.md
2. Compose email based on user request
3. Confirm with user before sending (recipients, subject, content summary)
4. Execute `scripts/send_email.py`
5. Report result

## Security

- Never log or display the full auth code
- Always confirm recipients and content before sending
- Credentials stay in TOOLS.md, never in SKILL.md or scripts
