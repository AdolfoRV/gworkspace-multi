import argparse

from core import _out, _err, build_service


# ─── Operations ──────────────────────────────────────────────────────────────

def create_space(svc) -> None:
    result = svc.spaces().create(body={}).execute()
    _out({
        "status": "created",
        "name": result.get("name"),
        "meetingUri": result.get("meetingUri"),
        "meetingCode": result.get("meetingCode"),
    })


def get_space(svc, space_name: str) -> None:
    _out(svc.spaces().get(name=space_name).execute())


def patch_space(svc, space_name: str, access_type: str = None, moderation: str = None) -> None:
    body: dict = {}
    config = {}
    if access_type:
        config["accessType"] = access_type
    if moderation:
        config["moderation"] = moderation
    
    if config:
        body["config"] = config
        
    result = svc.spaces().patch(name=space_name, body=body).execute()
    _out({"status": "patched", "name": result.get("name"), "config": result.get("config")})


def end_active_conference(svc, space_name: str) -> None:
    svc.spaces().endActiveConference(name=space_name, body={}).execute()
    _out({"status": "ended", "space": space_name})


# ─── Dispatch ─────────────────────────────────────────────────────────────────

def dispatch(profile: str, command: str, args: list) -> None:
    svc = build_service("meet", "v2", profile)
    p = argparse.ArgumentParser(prog=f"meet {command}")

    if command == "create-space":
        create_space(svc)

    elif command == "get-space":
        p.add_argument("space_name")
        a = p.parse_args(args)
        get_space(svc, a.space_name)

    elif command == "patch-space":
        p.add_argument("space_name")
        p.add_argument("--access-type")
        p.add_argument("--moderation")
        a = p.parse_args(args)
        patch_space(svc, a.space_name, a.access_type, a.moderation)

    elif command == "end-conference":
        p.add_argument("space_name")
        a = p.parse_args(args)
        end_active_conference(svc, a.space_name)

    else:
        _err(f"Unknown meet command: {command}")
