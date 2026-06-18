import json
import sys


def _out(data) -> None:
    print(json.dumps(data, ensure_ascii=False, default=str), flush=True)


def _err(msg: str, code: int = 1) -> None:
    print(json.dumps({"status": "error", "error": msg}), flush=True)
    sys.exit(code)
