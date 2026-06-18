import argparse

from core import _out, _err, build_service


# ─── Operations ──────────────────────────────────────────────────────────────

def list_lists(svc) -> None:
    resp = svc.tasklists().list().execute()
    _out(resp.get("items", []))


def list_tasks(svc, tasklist_id: str = "@default",
               show_completed: bool = False, max_results: int = 50) -> None:
    resp = svc.tasks().list(
        tasklist=tasklist_id,
        showCompleted=show_completed,
        maxResults=max_results,
    ).execute()
    _out(resp.get("items", []))


def create(svc, title: str, notes: str = None,
           due: str = None, tasklist_id: str = "@default") -> None:
    body: dict = {"title": title}
    if notes:
        body["notes"] = notes
    if due:
        body["due"] = due
    result = svc.tasks().insert(tasklist=tasklist_id, body=body).execute()
    _out({
        "status": "created",
        "id": result["id"],
        "title": result.get("title"),
        "due": result.get("due"),
        "task_status": result.get("status"),
    })


def complete(svc, task_id: str, tasklist_id: str = "@default") -> None:
    result = svc.tasks().patch(
        tasklist=tasklist_id, task=task_id, body={"status": "completed"}
    ).execute()
    _out({"status": "completed", "id": result["id"], "title": result.get("title")})


def delete(svc, task_id: str, tasklist_id: str = "@default") -> None:
    svc.tasks().delete(tasklist=tasklist_id, task=task_id).execute()
    _out({"status": "deleted", "taskId": task_id})


# ─── Dispatch ─────────────────────────────────────────────────────────────────

def dispatch(profile: str, command: str, args: list) -> None:
    svc = build_service("tasks", "v1", profile)
    p = argparse.ArgumentParser(prog=f"tasks {command}")

    if command == "list-lists":
        list_lists(svc)

    elif command == "list":
        p.add_argument("--tasklist", default="@default")
        p.add_argument("--show-completed", action="store_true")
        p.add_argument("--max", type=int, default=50)
        a = p.parse_args(args)
        list_tasks(svc, a.tasklist, a.show_completed, a.max)

    elif command == "create":
        p.add_argument("--title", required=True)
        p.add_argument("--notes")
        p.add_argument("--due")
        p.add_argument("--tasklist", default="@default")
        a = p.parse_args(args)
        create(svc, a.title, a.notes, a.due, a.tasklist)

    elif command == "complete":
        p.add_argument("task_id")
        p.add_argument("--tasklist", default="@default")
        a = p.parse_args(args)
        complete(svc, a.task_id, a.tasklist)

    elif command == "delete":
        p.add_argument("task_id")
        p.add_argument("--tasklist", default="@default")
        a = p.parse_args(args)
        delete(svc, a.task_id, a.tasklist)

    else:
        _err(f"Unknown tasks command: {command}")
