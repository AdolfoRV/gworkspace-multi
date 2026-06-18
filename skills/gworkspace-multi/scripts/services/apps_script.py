import argparse
import json

from core import _out, _err, build_service


# ─── Operations ──────────────────────────────────────────────────────────────

def run(svc, script_id: str, function_name: str, parameters: list = None) -> None:
    body: dict = {"function": function_name, "devMode": False}
    if parameters:
        body["parameters"] = parameters
    try:
        resp = svc.scripts().run(scriptId=script_id, body=body).execute()
        if "error" in resp:
            _out({"status": "script_error", "error": resp["error"]})
        else:
            _out({"status": "ok", "response": resp.get("response", {}).get("result")})
    except Exception as e:
        _err(str(e))


def get_project(svc, script_id: str) -> None:
    _out(svc.projects().get(scriptId=script_id).execute())


def get_content(svc, script_id: str) -> None:
    _out(svc.projects().getContent(scriptId=script_id).execute())


# ─── Dispatch ─────────────────────────────────────────────────────────────────

def dispatch(profile: str, command: str, args: list) -> None:
    svc = build_service("script", "v1", profile)
    p = argparse.ArgumentParser(prog=f"scripts {command}")

    if command == "run":
        p.add_argument("script_id")
        p.add_argument("--function", required=True, dest="function_name")
        p.add_argument("--params")
        a = p.parse_args(args)
        params = None
        if a.params:
            try:
                params = json.loads(a.params)
                if not isinstance(params, list):
                    _err("--params must be a JSON array, e.g. '[\"arg1\", 42]'")
            except json.JSONDecodeError as e:
                _err(f"Invalid JSON in --params: {e}")
        run(svc, a.script_id, a.function_name, params)

    elif command == "get-project":
        p.add_argument("script_id")
        a = p.parse_args(args)
        get_project(svc, a.script_id)

    elif command == "get-content":
        p.add_argument("script_id")
        a = p.parse_args(args)
        get_content(svc, a.script_id)

    else:
        _err(f"Unknown scripts command: {command}")
