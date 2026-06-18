import argparse

from core import _out, _err, build_service


# ─── Operations ──────────────────────────────────────────────────────────────

def get(svc, doc_id: str) -> None:
    doc = svc.documents().get(documentId=doc_id).execute()
    text = ""
    for elem in doc.get("body", {}).get("content", []):
        if "paragraph" in elem:
            for pe in elem["paragraph"].get("elements", []):
                text += pe.get("textRun", {}).get("content", "")
    _out({
        "documentId": doc["documentId"],
        "title": doc.get("title", ""),
        "text": text,
        "revisionId": doc.get("revisionId"),
    })


def create(svc, title: str, body_text: str = None) -> None:
    doc = svc.documents().create(body={"title": title}).execute()
    doc_id = doc["documentId"]
    if body_text:
        svc.documents().batchUpdate(documentId=doc_id, body={
            "requests": [{"insertText": {"location": {"index": 1}, "text": body_text}}]
        }).execute()
    _out({
        "status": "created",
        "documentId": doc_id,
        "title": doc.get("title"),
        "url": f"https://docs.google.com/document/d/{doc_id}/edit",
    })


def append(svc, doc_id: str, text: str) -> None:
    doc = svc.documents().get(documentId=doc_id).execute()
    content = doc.get("body", {}).get("content", [])
    end_index = content[-1].get("endIndex", 1) - 1 if content else 1
    svc.documents().batchUpdate(documentId=doc_id, body={
        "requests": [{"insertText": {"location": {"index": end_index}, "text": text}}]
    }).execute()
    _out({"status": "appended", "documentId": doc_id, "inserted_at": end_index, "characters": len(text)})


# ─── Dispatch ─────────────────────────────────────────────────────────────────

def dispatch(profile: str, command: str, args: list) -> None:
    svc = build_service("docs", "v1", profile)
    p = argparse.ArgumentParser(prog=f"docs {command}")

    if command == "get":
        p.add_argument("doc_id")
        a = p.parse_args(args)
        get(svc, a.doc_id)

    elif command == "create":
        p.add_argument("--title", required=True)
        p.add_argument("--body")
        a = p.parse_args(args)
        create(svc, a.title, a.body)

    elif command == "append":
        p.add_argument("doc_id")
        p.add_argument("--text", required=True)
        a = p.parse_args(args)
        append(svc, a.doc_id, a.text)

    else:
        _err(f"Unknown docs command: {command}")
