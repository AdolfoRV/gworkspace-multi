import argparse

from core import _out, _err, build_service


# ─── Operations ──────────────────────────────────────────────────────────────

def list_events(svc, start: str = None, end: str = None,
                calendar_id: str = "primary", max_results: int = 50) -> None:
    from datetime import datetime, timezone
    kwargs = {
        "calendarId": calendar_id,
        "timeMin": start or datetime.now(timezone.utc).isoformat(),
        "maxResults": max_results,
        "singleEvents": True,
        "orderBy": "startTime",
    }
    if end:
        kwargs["timeMax"] = end
    resp = svc.events().list(**kwargs).execute()
    _out([
        {
            "id": e["id"],
            "summary": e.get("summary", ""),
            "start": e.get("start", {}).get("dateTime") or e.get("start", {}).get("date"),
            "end": e.get("end", {}).get("dateTime") or e.get("end", {}).get("date"),
            "location": e.get("location", ""),
            "description": e.get("description", ""),
            "htmlLink": e.get("htmlLink", ""),
            "attendees": [a.get("email") for a in e.get("attendees", [])],
        }
        for e in resp.get("items", [])
    ])


def list_calendars(svc) -> None:
    resp = svc.calendarList().list().execute()
    _out([
        {"id": c["id"], "summary": c.get("summary"), "primary": c.get("primary", False)}
        for c in resp.get("items", [])
    ])


def create(svc, summary: str, start: str, end: str, location: str = None,
           description: str = None, attendees: str = None,
           calendar_id: str = "primary", create_meet: bool = False, profile: str = None) -> None:
    body: dict = {
        "summary": summary,
        "start": {"dateTime": start},
        "end": {"dateTime": end},
    }
    if location:
        body["location"] = location
    if description:
        body["description"] = description
    if attendees:
        body["attendees"] = [{"email": e.strip()} for e in attendees.split(",")]
    if create_meet:
        body["conferenceData"] = {
            "createRequest": {"requestId": f"meet-{start[:10]}-{summary[:5]}"}
        }

    result = svc.events().insert(
        calendarId=calendar_id,
        body=body,
        conferenceDataVersion="1" if create_meet else None,
    ).execute()

    out_data = {
        "status": "created",
        "id": result["id"],
        "summary": result.get("summary"),
        "htmlLink": result.get("htmlLink"),
        "conferenceData": result.get("conferenceData"),
    }

    # Resolve internal space_id if Meet was created
    if create_meet and profile and "conferenceData" in result:
        try:
            # Initialize Meet service to get the official resource name
            meet_svc = build_service("meet", "v2", profile)
            conf_id = result["conferenceData"].get("conferenceId")
            if conf_id:
                # Validate and fetch the actual space object
                space = meet_svc.spaces().get(name=f"spaces/{conf_id}").execute()
                out_data["space_id"] = space["name"]
        except Exception:
            # Fallback: Construct the space ID from conferenceId if get() fails (propagation delay)
            conf_id = result.get("conferenceData", {}).get("conferenceId")
            out_data["space_id"] = f"spaces/{conf_id}" if conf_id else None

    _out(out_data)


def update(svc, event_id: str, calendar_id: str = "primary", summary: str = None,
           start: str = None, end: str = None, location: str = None,
           description: str = None, attendees: str = None) -> None:
    event = svc.events().get(calendarId=calendar_id, eventId=event_id).execute()

    if summary:
        event["summary"] = summary
    if start:
        event["start"] = {"dateTime": start, "timeZone": event.get("start", {}).get("timeZone", "UTC")}
    if end:
        event["end"] = {"dateTime": end, "timeZone": event.get("end", {}).get("timeZone", "UTC")}
    if location is not None:
        event["location"] = location
    if description is not None:
        event["description"] = description
    if attendees is not None:
        event["attendees"] = [{"email": e.strip()} for e in attendees.split(",")]

    result = svc.events().update(
        calendarId=calendar_id, eventId=event_id, body=event, sendUpdates="none"
    ).execute()
    _out({
        "status": "updated",
        "id": result["id"],
        "summary": result.get("summary"),
        "start": result.get("start"),
        "end": result.get("end"),
        "htmlLink": result.get("htmlLink"),
    })


def delete(svc, event_id: str, calendar_id: str = "primary") -> None:
    svc.events().delete(calendarId=calendar_id, eventId=event_id).execute()
    _out({"status": "deleted", "eventId": event_id})


# ─── Dispatch ─────────────────────────────────────────────────────────────────

def dispatch(profile: str, command: str, args: list) -> None:
    svc = build_service("calendar", "v3", profile)
    p = argparse.ArgumentParser(prog=f"calendar {command}")

    if command == "list":
        p.add_argument("--start")
        p.add_argument("--end")
        p.add_argument("--calendar-id", default="primary")
        p.add_argument("--max", type=int, default=50)
        a = p.parse_args(args)
        list_events(svc, a.start, a.end, a.calendar_id, a.max)

    elif command == "list-calendars":
        list_calendars(svc)

    elif command == "create":
        p.add_argument("--summary", required=True)
        p.add_argument("--start", required=True)
        p.add_argument("--end", required=True)
        p.add_argument("--location")
        p.add_argument("--description")
        p.add_argument("--attendees")
        p.add_argument("--calendar-id", default="primary")
        p.add_argument("--create-meet", action="store_true")
        a = p.parse_args(args)
        create(svc, a.summary, a.start, a.end, a.location, a.description,
               a.attendees, a.calendar_id, a.create_meet, profile=profile)

    elif command == "update":
        p.add_argument("event_id")
        p.add_argument("--summary")
        p.add_argument("--start")
        p.add_argument("--end")
        p.add_argument("--location")
        p.add_argument("--description")
        p.add_argument("--attendees")
        p.add_argument("--calendar-id", default="primary")
        a = p.parse_args(args)
        update(svc, a.event_id, a.calendar_id, a.summary, a.start, a.end,
               a.location, a.description, a.attendees)

    elif command == "delete":
        p.add_argument("event_id")
        p.add_argument("--calendar-id", default="primary")
        a = p.parse_args(args)
        delete(svc, a.event_id, a.calendar_id)

    else:
        _err(f"Unknown calendar command: {command}")
