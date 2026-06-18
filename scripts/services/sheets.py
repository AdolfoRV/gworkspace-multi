import argparse
import json

from core import _out, _err, build_service


# ─── Operations ──────────────────────────────────────────────────────────────

def create(svc, title: str, sheet_name: str = None) -> None:
    body: dict = {"properties": {"title": title}}
    if sheet_name:
        body["sheets"] = [{"properties": {"title": sheet_name}}]
    result = svc.spreadsheets().create(body=body).execute()
    _out({
        "status": "created",
        "spreadsheetId": result["spreadsheetId"],
        "title": title,
        "spreadsheetUrl": result.get("spreadsheetUrl"),
    })


def get(svc, sheet_id: str, range_: str) -> None:
    resp = svc.spreadsheets().values().get(spreadsheetId=sheet_id, range=range_).execute()
    _out(resp.get("values", []))


def update(svc, sheet_id: str, range_: str, values: list) -> None:
    resp = svc.spreadsheets().values().update(
        spreadsheetId=sheet_id,
        range=range_,
        valueInputOption="USER_ENTERED",
        body={"values": values},
    ).execute()
    _out({
        "status": "updated",
        "updatedRange": resp.get("updatedRange"),
        "updatedRows": resp.get("updatedRows"),
        "updatedCells": resp.get("updatedCells"),
    })


def append(svc, sheet_id: str, range_: str, values: list) -> None:
    resp = svc.spreadsheets().values().append(
        spreadsheetId=sheet_id,
        range=range_,
        valueInputOption="USER_ENTERED",
        insertDataOption="INSERT_ROWS",
        body={"values": values},
    ).execute()
    _out({
        "status": "appended",
        "updatedRange": resp.get("updates", {}).get("updatedRange"),
        "updatedRows": resp.get("updates", {}).get("updatedRows"),
    })


# ─── Dispatch ─────────────────────────────────────────────────────────────────

def dispatch(profile: str, command: str, args: list) -> None:
    svc = build_service("sheets", "v4", profile)
    p = argparse.ArgumentParser(prog=f"sheets {command}")

    if command == "create":
        p.add_argument("--title", required=True)
        p.add_argument("--sheet-name")
        a = p.parse_args(args)
        create(svc, a.title, a.sheet_name)

    elif command == "get":
        p.add_argument("sheet_id")
        p.add_argument("range")
        a = p.parse_args(args)
        get(svc, a.sheet_id, a.range)

    elif command == "update":
        p.add_argument("sheet_id")
        p.add_argument("range")
        p.add_argument("--values", required=True)
        a = p.parse_args(args)
        update(svc, a.sheet_id, a.range, json.loads(a.values))

    elif command == "append":
        p.add_argument("sheet_id")
        p.add_argument("range")
        p.add_argument("--values", required=True)
        a = p.parse_args(args)
        append(svc, a.sheet_id, a.range, json.loads(a.values))

    else:
        _err(f"Unknown sheets command: {command}")
