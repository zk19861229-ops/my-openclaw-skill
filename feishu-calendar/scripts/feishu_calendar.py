#!/usr/bin/env python3
"""Feishu Calendar management via Open API v4."""

import argparse
import json
import sys
import time
import urllib.request
import urllib.error
from datetime import datetime, timezone, timedelta

FEISHU_HOST = "https://open.feishu.cn"
TZ = timezone(timedelta(hours=8))


def get_tenant_token(app_id: str, app_secret: str) -> str:
    url = f"{FEISHU_HOST}/open-apis/auth/v3/tenant_access_token/internal"
    data = json.dumps({"app_id": app_id, "app_secret": app_secret}).encode()
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=15) as resp:
        body = json.loads(resp.read())
    if body.get("code") != 0:
        raise RuntimeError(f"Failed to get token: {body}")
    return body["tenant_access_token"]


def api(token: str, method: str, path: str, body=None, params=None):
    url = f"{FEISHU_HOST}/open-apis{path}"
    if params:
        qs = "&".join(f"{k}={v}" for k, v in params.items() if v is not None)
        if qs:
            url += f"?{qs}"
    data = json.dumps(body).encode() if body else None
    req = urllib.request.Request(url, data=data, method=method, headers={
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    })
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read())


def ts_to_str(ts):
    if ts is None:
        return ""
    try:
        return datetime.fromtimestamp(int(ts), tz=TZ).strftime("%Y-%m-%d %H:%M")
    except (ValueError, TypeError, OSError):
        return str(ts)


def parse_time(s: str) -> str:
    """Parse user time string to unix timestamp string."""
    for fmt in ["%Y-%m-%d %H:%M", "%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M", "%Y-%m-%dT%H:%M:%S"]:
        try:
            dt = datetime.strptime(s, fmt).replace(tzinfo=TZ)
            return str(int(dt.timestamp()))
        except ValueError:
            continue
    # try date only (all day)
    try:
        dt = datetime.strptime(s, "%Y-%m-%d").replace(tzinfo=TZ)
        return str(int(dt.timestamp()))
    except ValueError:
        pass
    raise ValueError(f"Cannot parse time: {s}")


# ── Commands ──────────────────────────────────────────────

def cmd_list_calendars(token, args):
    resp = api(token, "GET", "/calendar/v4/calendars", params={"page_size": "50"})
    cals = resp.get("data", {}).get("calendar_list", [])
    results = []
    for c in cals:
        results.append({
            "id": c.get("calendar_id"),
            "summary": c.get("summary"),
            "type": c.get("type"),
            "role": c.get("role"),
        })
    print(json.dumps(results, ensure_ascii=False, indent=2))


def resolve_calendar_id(token, cal_id):
    """Resolve 'primary' to actual calendar ID."""
    if cal_id and cal_id != "primary":
        return cal_id
    resp = api(token, "GET", "/calendar/v4/calendars", params={"page_size": "50"})
    cals = resp.get("data", {}).get("calendar_list", [])
    for c in cals:
        if c.get("type") == "primary":
            return c["calendar_id"]
    if cals:
        return cals[0]["calendar_id"]
    raise RuntimeError("No calendars found")


def cmd_list_events(token, args):
    cal_id = resolve_calendar_id(token, args.calendar_id)
    params = {"page_size": "50"}
    if args.start:
        params["start_time"] = parse_time(args.start)
    else:
        # default: today start
        today = datetime.now(TZ).replace(hour=0, minute=0, second=0, microsecond=0)
        params["start_time"] = str(int(today.timestamp()))
    if args.end:
        params["end_time"] = parse_time(args.end)
    else:
        # default: 7 days from start
        params["end_time"] = str(int(params["start_time"]) + 7 * 86400)

    resp = api(token, "GET", f"/calendar/v4/calendars/{cal_id}/events", params=params)
    events = resp.get("data", {}).get("items", [])
    results = []
    for e in events:
        st = e.get("start_time", {})
        et = e.get("end_time", {})
        results.append({
            "event_id": e.get("event_id"),
            "summary": e.get("summary"),
            "start": ts_to_str(st.get("timestamp")),
            "end": ts_to_str(et.get("timestamp")),
            "status": e.get("status"),
            "location": (e.get("location") or {}).get("name", ""),
            "description": (e.get("description") or "")[:200],
        })
    print(json.dumps(results, ensure_ascii=False, indent=2))


def cmd_create_event(token, args):
    cal_id = resolve_calendar_id(token, args.calendar_id)
    body = {
        "summary": args.summary,
        "start_time": {"timestamp": parse_time(args.start)},
        "end_time": {"timestamp": parse_time(args.end)},
    }
    if args.description:
        body["description"] = args.description
    if args.location:
        body["location"] = {"name": args.location}
    if args.attendees:
        body["attendee_ability"] = "can_modify_event"
    resp = api(token, "POST", f"/calendar/v4/calendars/{cal_id}/events", body=body)
    event = resp.get("data", {}).get("event", {})

    # Add attendees if specified
    if args.attendees and event.get("event_id"):
        eid = event["event_id"]
        attendee_list = []
        for a in args.attendees:
            if a.startswith("ou_"):
                attendee_list.append({"type": "user", "user_id": a})
            elif "@" in a:
                attendee_list.append({"type": "third_party", "third_party_email": a})
            else:
                attendee_list.append({"type": "user", "user_id": a})
        api(token, "POST", f"/calendar/v4/calendars/{cal_id}/events/{eid}/attendees",
            body={"attendees": attendee_list})

    print(json.dumps({
        "status": "created",
        "event_id": event.get("event_id"),
        "summary": event.get("summary"),
        "start": ts_to_str(event.get("start_time", {}).get("timestamp")),
        "end": ts_to_str(event.get("end_time", {}).get("timestamp")),
    }, ensure_ascii=False, indent=2))


def cmd_delete_event(token, args):
    cal_id = resolve_calendar_id(token, args.calendar_id)
    resp = api(token, "DELETE", f"/calendar/v4/calendars/{cal_id}/events/{args.event_id}")
    print(json.dumps({"status": "deleted", "event_id": args.event_id}, ensure_ascii=False))


def cmd_update_event(token, args):
    cal_id = resolve_calendar_id(token, args.calendar_id)
    body = {}
    if args.summary:
        body["summary"] = args.summary
    if args.start:
        body["start_time"] = {"timestamp": parse_time(args.start)}
    if args.end:
        body["end_time"] = {"timestamp": parse_time(args.end)}
    if args.description:
        body["description"] = args.description
    if args.location:
        body["location"] = {"name": args.location}
    if not body:
        print(json.dumps({"error": "nothing to update"}))
        return
    resp = api(token, "PATCH", f"/calendar/v4/calendars/{cal_id}/events/{args.event_id}", body=body)
    event = resp.get("data", {}).get("event", {})
    print(json.dumps({
        "status": "updated",
        "event_id": event.get("event_id"),
        "summary": event.get("summary"),
    }, ensure_ascii=False, indent=2))


# ── Main ──────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Feishu Calendar Manager")
    parser.add_argument("--app-id", required=True)
    parser.add_argument("--app-secret", required=True)
    sub = parser.add_subparsers(dest="command", required=True)

    # list-calendars
    sub.add_parser("list-calendars", help="List all calendars")

    # list-events
    p_list = sub.add_parser("list-events", help="List events")
    p_list.add_argument("--calendar-id", default="primary")
    p_list.add_argument("--start", help="Start time (YYYY-MM-DD HH:MM)")
    p_list.add_argument("--end", help="End time (YYYY-MM-DD HH:MM)")

    # create-event
    p_create = sub.add_parser("create-event", help="Create event")
    p_create.add_argument("--calendar-id", default="primary")
    p_create.add_argument("--summary", required=True, help="Event title")
    p_create.add_argument("--start", required=True, help="Start time")
    p_create.add_argument("--end", required=True, help="End time")
    p_create.add_argument("--description", help="Event description")
    p_create.add_argument("--location", help="Event location")
    p_create.add_argument("--attendees", nargs="*", help="Attendee open_ids or emails")

    # update-event
    p_update = sub.add_parser("update-event", help="Update event")
    p_update.add_argument("--calendar-id", default="primary")
    p_update.add_argument("--event-id", required=True)
    p_update.add_argument("--summary")
    p_update.add_argument("--start")
    p_update.add_argument("--end")
    p_update.add_argument("--description")
    p_update.add_argument("--location")

    # delete-event
    p_del = sub.add_parser("delete-event", help="Delete event")
    p_del.add_argument("--calendar-id", default="primary")
    p_del.add_argument("--event-id", required=True)

    args = parser.parse_args()
    token = get_tenant_token(args.app_id, args.app_secret)

    cmds = {
        "list-calendars": cmd_list_calendars,
        "list-events": cmd_list_events,
        "create-event": cmd_create_event,
        "update-event": cmd_update_event,
        "delete-event": cmd_delete_event,
    }
    cmds[args.command](token, args)


if __name__ == "__main__":
    main()
