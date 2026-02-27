---
name: feishu-calendar
description: Manage Feishu/Lark calendar events. Use when user asks to check schedule, create/update/delete calendar events, view upcoming meetings, manage agenda, or anything related to Feishu calendar and scheduling. Triggers: 日程, 日历, 会议, 安排, schedule, calendar, meeting, agenda.
---

# Feishu Calendar

Manage Feishu calendar via `scripts/feishu_calendar.py`.

## Credentials

Read `app_id` and `app_secret` from OpenClaw config (`~/.openclaw/openclaw.json` feishu section):
- app_id: `cli_a90759d13b38dbcc`
- app_secret: read from config at runtime

Store in TOOLS.md if needed for quick reference.

## Commands

All commands require `--app-id` and `--app-secret`.

### List Calendars

```bash
python scripts/feishu_calendar.py --app-id ID --app-secret SECRET list-calendars
```

### List Events

```bash
python scripts/feishu_calendar.py --app-id ID --app-secret SECRET list-events \
  [--calendar-id CAL_ID] [--start "2026-02-25 09:00"] [--end "2026-03-01 18:00"]
```

- Default calendar: `primary`
- Default range: today → 7 days ahead

### Create Event

```bash
python scripts/feishu_calendar.py --app-id ID --app-secret SECRET create-event \
  --summary "Meeting Title" --start "2026-02-26 14:00" --end "2026-02-26 15:00" \
  [--description "Details"] [--location "Room A"] [--attendees ou_xxx user@example.com]
```

- Attendees: pass open_id (ou_xxx) or email addresses
- Time format: `YYYY-MM-DD HH:MM`

### Update Event

```bash
python scripts/feishu_calendar.py --app-id ID --app-secret SECRET update-event \
  --event-id EVENT_ID [--summary "New Title"] [--start "..."] [--end "..."] \
  [--description "..."] [--location "..."]
```

### Delete Event

```bash
python scripts/feishu_calendar.py --app-id ID --app-secret SECRET delete-event \
  --event-id EVENT_ID
```

## Workflow

1. Read feishu credentials from config
2. Understand user's calendar request
3. Execute appropriate command
4. Present results in readable format (convert timestamps, summarize)
5. For create/update/delete: confirm with user before executing

## Notes

- Calendar ID `primary` refers to the user's main calendar
- All times are in Asia/Shanghai (UTC+8)
- The script outputs JSON for easy parsing
