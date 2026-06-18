import argparse
import base64
import json
import re
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from core import _out, _err, build_service


# ─── Helpers ─────────────────────────────────────────────────────────────────

def _extract_headers(msg: dict, *names: str) -> dict:
    return {
        h["name"]: h["value"]
        for h in msg.get("payload", {}).get("headers", [])
        if h["name"] in names
    }


def _extract_body(payload: dict) -> str:
    if payload.get("body", {}).get("data"):
        return base64.urlsafe_b64decode(payload["body"]["data"]).decode("utf-8", errors="replace")
    for part in payload.get("parts", []):
        if part.get("mimeType") in ("text/plain", "text/html"):
            data = part.get("body", {}).get("data", "")
            if data:
                return base64.urlsafe_b64decode(data).decode("utf-8", errors="replace")
        if "parts" in part:
            result = _extract_body(part)
            if result:
                return result
    return ""


def _build_mime(to: str, subject: str, body: str,
                sender: str = None, html: bool = False) -> MIMEText | MIMEMultipart:
    if html:
        plain_fallback = re.sub(r"<[^>]+>", "", body).strip()
        msg = MIMEMultipart("alternative")
        msg.attach(MIMEText(plain_fallback, "plain"))
        msg.attach(MIMEText(body, "html"))
    else:
        msg = MIMEText(body, "plain")
    msg["To"] = to
    msg["Subject"] = subject
    if sender:
        msg["From"] = sender
    return msg


def _encode_raw(msg) -> str:
    return base64.urlsafe_b64encode(msg.as_bytes()).decode()


# ─── Operations ──────────────────────────────────────────────────────────────

def search(svc, query: str, max_results: int) -> None:
    resp = svc.users().messages().list(userId="me", q=query, maxResults=max_results).execute()
    results = []
    for m in resp.get("messages", []):
        msg = svc.users().messages().get(
            userId="me", id=m["id"], format="metadata",
            metadataHeaders=["From", "To", "Subject", "Date"],
        ).execute()
        headers = _extract_headers(msg, "From", "To", "Subject", "Date")
        results.append({
            "id": msg["id"],
            "threadId": msg.get("threadId"),
            "from": headers.get("From", ""),
            "to": headers.get("To", ""),
            "subject": headers.get("Subject", ""),
            "date": headers.get("Date", ""),
            "snippet": msg.get("snippet", ""),
            "labels": msg.get("labelIds", []),
        })
    _out(results)


def get(svc, message_id: str) -> None:
    msg = svc.users().messages().get(userId="me", id=message_id, format="full").execute()
    headers = _extract_headers(msg, "From", "To", "Subject", "Date")
    _out({
        "id": msg["id"],
        "threadId": msg.get("threadId"),
        "from": headers.get("From", ""),
        "to": headers.get("To", ""),
        "subject": headers.get("Subject", ""),
        "date": headers.get("Date", ""),
        "labels": msg.get("labelIds", []),
        "body": _extract_body(msg.get("payload", {})),
    })


def send(svc, to: str, subject: str, body: str,
         sender: str = None, html: bool = False, reply_to: str = None) -> None:
    msg = _build_mime(to, subject, body, sender, html)
    if reply_to:
        msg["In-Reply-To"] = reply_to
        msg["References"] = reply_to
    result = svc.users().messages().send(userId="me", body={"raw": _encode_raw(msg)}).execute()
    _out({"status": "sent", "id": result["id"], "threadId": result.get("threadId")})


def reply(svc, message_id: str, body: str, sender: str = None) -> None:
    orig = svc.users().messages().get(
        userId="me", id=message_id, format="metadata",
        metadataHeaders=["From", "Subject", "Message-ID", "References"],
    ).execute()
    headers = _extract_headers(orig, "From", "Subject", "Message-ID", "References")
    thread_id = orig.get("threadId")

    msg = MIMEText(body, "plain")
    msg["To"] = headers.get("From", "")
    msg["Subject"] = "Re: " + headers.get("Subject", "")
    msg_id = headers.get("Message-ID", "")
    msg["In-Reply-To"] = msg_id
    msg["References"] = (headers.get("References", "") + " " + msg_id).strip()
    if sender:
        msg["From"] = sender

    result = svc.users().messages().send(
        userId="me", body={"raw": _encode_raw(msg), "threadId": thread_id}
    ).execute()
    _out({"status": "sent", "id": result["id"], "threadId": result.get("threadId")})


def labels(svc) -> None:
    resp = svc.users().labels().list(userId="me").execute()
    _out(resp.get("labels", []))


def modify(svc, message_id: str, add_labels: list, remove_labels: list) -> None:
    body = {}
    if add_labels:
        body["addLabelIds"] = add_labels
    if remove_labels:
        body["removeLabelIds"] = remove_labels
    result = svc.users().messages().modify(userId="me", id=message_id, body=body).execute()
    _out({"status": "modified", "id": result["id"], "labels": result.get("labelIds", [])})


def get_attachments(svc, message_id: str, output_dir: str = None) -> None:
    from pathlib import Path
    out_path = Path(output_dir).expanduser() if output_dir else Path.home() / "Downloads"
    out_path.mkdir(parents=True, exist_ok=True)

    msg = svc.users().messages().get(userId="me", id=message_id, format="full").execute()

    def _extract_parts(payload):
        parts = []
        if payload.get("filename") and payload.get("body", {}).get("attachmentId"):
            parts.append(payload)
        for part in payload.get("parts", []):
            parts.extend(_extract_parts(part))
        return parts

    attachment_parts = _extract_parts(msg.get("payload", {}))
    if not attachment_parts:
        _out({"status": "no_attachments", "messageId": message_id})
        return

    saved = []
    for part in attachment_parts:
        att = svc.users().messages().attachments().get(
            userId="me", messageId=message_id, id=part["body"]["attachmentId"]
        ).execute()
        data = base64.urlsafe_b64decode(att["data"])
        dest = out_path / part["filename"]
        dest.write_bytes(data)
        saved.append({"filename": part["filename"], "path": str(dest), "size": len(data)})

    _out({"status": "saved", "messageId": message_id, "attachments": saved})


def draft_create(svc, to: str, subject: str, body: str,
                 sender: str = None, html: bool = False, reply_to_id: str = None) -> None:
    msg = _build_mime(to, subject, body, sender, html)
    draft_body: dict = {"message": {"raw": _encode_raw(msg)}}

    if reply_to_id:
        orig = svc.users().messages().get(
            userId="me", id=reply_to_id, format="metadata",
            metadataHeaders=["Message-ID", "References"],
        ).execute()
        headers = _extract_headers(orig, "Message-ID", "References")
        msg["In-Reply-To"] = headers.get("Message-ID", "")
        msg["References"] = (
            headers.get("References", "") + " " + headers.get("Message-ID", "")
        ).strip()
        draft_body["message"]["raw"] = _encode_raw(msg)
        draft_body["message"]["threadId"] = orig.get("threadId")

    result = svc.users().drafts().create(userId="me", body=draft_body).execute()
    _out({"status": "draft_created", "draftId": result["id"],
          "messageId": result.get("message", {}).get("id")})


def draft_send(svc, draft_id: str) -> None:
    result = svc.users().drafts().send(userId="me", body={"id": draft_id}).execute()
    _out({"status": "sent", "id": result["id"], "threadId": result.get("threadId")})


def schedule(svc, to: str, subject: str, body: str, send_at: str,
             sender: str = None, html: bool = False) -> None:
    from datetime import datetime, timezone

    try:
        dt = datetime.fromisoformat(send_at.replace("Z", "+00:00"))
    except ValueError:
        _err(
            f"Formato de fecha inválido: '{send_at}'. "
            "Usar ISO8601, ej. 2026-06-20T15:00:00Z"
        )

    if dt.tzinfo is None:
        _err(
            "La fecha debe incluir timezone, "
            "ej. 2026-06-20T15:00:00Z o 2026-06-20T12:00:00-03:00"
        )

    if dt <= datetime.now(timezone.utc):
        _err(f"La fecha debe ser futura. Recibido: {send_at}")

    msg = _build_mime(to, subject, body, sender, html)
    draft_body = {"message": {"raw": _encode_raw(msg)}}
    draft = svc.users().drafts().create(userId="me", body=draft_body).execute()
    draft_id = draft["id"]
    message_id = draft.get("message", {}).get("id")

    send_at_unix = int(dt.timestamp())

    at_command = (
        f'echo "python3 $HERMES_SKILL_DIR/scripts/google_api.py '
        f'--profile $PROFILE gmail draft-send {draft_id}" '
        f"| at -t {dt.strftime('%Y%m%d%H%M')}"
    )

    _out({
        "status": "draft_created",
        "draftId": draft_id,
        "messageId": message_id,
        "send_at": send_at,
        "send_at_unix": send_at_unix,
        "note": (
            "La API de Gmail no expone scheduled send. "
            "El borrador está listo — enviarlo con draft-send en la fecha indicada."
        ),
        "at_command": at_command,
    })


# ─── Dispatch ─────────────────────────────────────────────────────────────────

def dispatch(profile: str, command: str, args: list) -> None:
    svc = build_service("gmail", "v1", profile)
    p = argparse.ArgumentParser(prog=f"gmail {command}")

    if command == "search":
        p.add_argument("query")
        p.add_argument("--max", type=int, default=10)
        a = p.parse_args(args)
        search(svc, a.query, a.max)

    elif command == "get":
        p.add_argument("message_id")
        a = p.parse_args(args)
        get(svc, a.message_id)

    elif command == "send":
        p.add_argument("--to", required=True)
        p.add_argument("--subject", required=True)
        p.add_argument("--body", required=True)
        p.add_argument("--from", dest="sender")
        p.add_argument("--html", action="store_true")
        p.add_argument("--reply-to")
        a = p.parse_args(args)
        send(svc, a.to, a.subject, a.body, a.sender, a.html, a.reply_to)

    elif command == "reply":
        p.add_argument("message_id")
        p.add_argument("--body", required=True)
        p.add_argument("--from", dest="sender")
        a = p.parse_args(args)
        reply(svc, a.message_id, a.body, a.sender)

    elif command == "labels":
        labels(svc)

    elif command == "modify":
        p.add_argument("message_id")
        p.add_argument("--add-labels", nargs="+", default=[])
        p.add_argument("--remove-labels", nargs="+", default=[])
        a = p.parse_args(args)
        modify(svc, a.message_id, a.add_labels, a.remove_labels)

    elif command == "get-attachments":
        p.add_argument("message_id")
        p.add_argument("--output")
        a = p.parse_args(args)
        get_attachments(svc, a.message_id, a.output)

    elif command == "draft-create":
        p.add_argument("--to", required=True)
        p.add_argument("--subject", required=True)
        p.add_argument("--body", required=True)
        p.add_argument("--from", dest="sender")
        p.add_argument("--html", action="store_true")
        p.add_argument("--reply-to-id")
        a = p.parse_args(args)
        draft_create(svc, a.to, a.subject, a.body, a.sender, a.html, a.reply_to_id)

    elif command == "draft-send":
        p.add_argument("draft_id")
        a = p.parse_args(args)
        draft_send(svc, a.draft_id)

    elif command == "schedule":
        p.add_argument("--to", required=True)
        p.add_argument("--subject", required=True)
        p.add_argument("--body", required=True)
        p.add_argument("--send-at", required=True)
        p.add_argument("--from", dest="sender")
        p.add_argument("--html", action="store_true")
        a = p.parse_args(args)
        schedule(svc, a.to, a.subject, a.body, a.send_at, a.sender, a.html)

    else:
        _err(f"Unknown gmail command: {command}")
