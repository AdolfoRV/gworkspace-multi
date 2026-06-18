import argparse
from pathlib import Path

from core import _out, _err, build_service


# ─── Operations ──────────────────────────────────────────────────────────────

def search(svc, query: str, max_results: int = 10, raw_query: bool = False) -> None:
    if raw_query:
        q = query
    else:
        escaped = query.replace("\\", "\\\\").replace("'", "\\'")
        q = f"fullText contains '{escaped}' and trashed=false"
    resp = svc.files().list(
        q=q,
        pageSize=max_results,
        fields="files(id,name,mimeType,modifiedTime,webViewLink,size)",
    ).execute()
    _out(resp.get("files", []))


def get(svc, file_id: str) -> None:
    result = svc.files().get(
        fileId=file_id,
        fields="id,name,mimeType,modifiedTime,size,webViewLink,parents,owners",
    ).execute()
    _out(result)


def upload(svc, local_path: str, name: str = None, parent_id: str = None) -> None:
    import mimetypes
    from googleapiclient.http import MediaFileUpload

    path = Path(local_path).expanduser()
    if not path.exists():
        _err(f"File not found: {path}")
    mime, _ = mimetypes.guess_type(str(path))
    meta = {"name": name or path.name}
    if parent_id:
        meta["parents"] = [parent_id]
    media = MediaFileUpload(str(path), mimetype=mime or "application/octet-stream", resumable=True)
    result = svc.files().create(body=meta, media_body=media, fields="id,name,mimeType,webViewLink").execute()
    _out({"status": "uploaded", **result})


def download(svc, file_id: str, output_path: str = None, export_mime: str = None) -> None:
    import io
    from googleapiclient.http import MediaIoBaseDownload

    EXPORT_DEFAULTS = {
        "application/vnd.google-apps.document":     ("application/pdf", ".pdf"),
        "application/vnd.google-apps.spreadsheet":  ("text/csv",        ".csv"),
        "application/vnd.google-apps.presentation": ("application/pdf", ".pdf"),
        "application/vnd.google-apps.drawing":      ("image/png",       ".png"),
    }

    meta = svc.files().get(fileId=file_id, fields="id,name,mimeType").execute()
    name, mime = meta["name"], meta["mimeType"]
    out_path = Path(output_path).expanduser() if output_path else Path.home() / "Downloads" / name
    out_path.parent.mkdir(parents=True, exist_ok=True)

    if mime.startswith("application/vnd.google-apps"):
        target_mime, ext = EXPORT_DEFAULTS.get(mime, ("application/pdf", ".pdf"))
        if export_mime:
            target_mime = export_mime
        if not output_path:
            out_path = out_path.with_suffix(ext)
        request = svc.files().export_media(fileId=file_id, mimeType=target_mime)
    else:
        request = svc.files().get_media(fileId=file_id)

    buf = io.BytesIO()
    downloader = MediaIoBaseDownload(buf, request)
    done = False
    while not done:
        _, done = downloader.next_chunk()

    out_path.write_bytes(buf.getvalue())
    _out({"status": "downloaded", "id": file_id, "name": name, "path": str(out_path), "mimeType": mime})


def create_folder(svc, name: str, parent_id: str = None) -> None:
    meta = {"name": name, "mimeType": "application/vnd.google-apps.folder"}
    if parent_id:
        meta["parents"] = [parent_id]
    result = svc.files().create(body=meta, fields="id,name,webViewLink").execute()
    _out({"status": "created", **result})


def share(svc, file_id: str, email: str = None, role: str = "reader",
          share_type: str = "user", domain: str = None, notify: bool = False) -> None:
    body: dict = {"role": role, "type": share_type}
    if share_type in ("user", "group") and email:
        body["emailAddress"] = email
    elif share_type == "domain" and domain:
        body["domain"] = domain
    result = svc.permissions().create(
        fileId=file_id, body=body, sendNotificationEmail=notify,
        fields="id,role,type",
    ).execute()
    _out({"status": "shared", "permissionId": result["id"], "fileId": file_id,
          "role": result.get("role"), "type": result.get("type")})


def delete(svc, file_id: str, permanent: bool = False) -> None:
    if permanent:
        svc.files().delete(fileId=file_id).execute()
        _out({"status": "deleted", "fileId": file_id, "permanent": True})
    else:
        svc.files().update(fileId=file_id, body={"trashed": True}).execute()
        _out({"status": "trashed", "fileId": file_id, "permanent": False})


def activity(svc_activity, item_name: str = None,
             ancestor_name: str = None, page_size: int = 10) -> None:
    body: dict = {"pageSize": page_size}
    if item_name:
        body["itemName"] = item_name
    if ancestor_name:
        body["ancestorName"] = ancestor_name
    resp = svc_activity.activity().query(body=body).execute()
    _out(resp.get("activities", []))


# ─── Dispatch ─────────────────────────────────────────────────────────────────

def dispatch(profile: str, command: str, args: list) -> None:
    from core.auth import build_service as _build
    svc = _build("drive", "v3", profile)
    p = argparse.ArgumentParser(prog=f"drive {command}")

    if command == "search":
        p.add_argument("query")
        p.add_argument("--max", type=int, default=10)
        p.add_argument("--raw-query", action="store_true")
        a = p.parse_args(args)
        search(svc, a.query, a.max, a.raw_query)

    elif command == "get":
        p.add_argument("file_id")
        a = p.parse_args(args)
        get(svc, a.file_id)

    elif command == "upload":
        p.add_argument("local_path")
        p.add_argument("--name")
        p.add_argument("--parent")
        a = p.parse_args(args)
        upload(svc, a.local_path, a.name, a.parent)

    elif command == "download":
        p.add_argument("file_id")
        p.add_argument("--output")
        p.add_argument("--export-mime")
        a = p.parse_args(args)
        download(svc, a.file_id, a.output, a.export_mime)

    elif command == "create-folder":
        p.add_argument("name")
        p.add_argument("--parent")
        a = p.parse_args(args)
        create_folder(svc, a.name, a.parent)

    elif command == "share":
        p.add_argument("file_id")
        p.add_argument("--email")
        p.add_argument("--role", default="reader")
        p.add_argument("--type", dest="share_type", default="user")
        p.add_argument("--domain")
        p.add_argument("--notify", action="store_true")
        a = p.parse_args(args)
        share(svc, a.file_id, a.email, a.role, a.share_type, a.domain, a.notify)

    elif command == "delete":
        p.add_argument("file_id")
        p.add_argument("--permanent", action="store_true")
        a = p.parse_args(args)
        delete(svc, a.file_id, a.permanent)

    elif command == "activity":
        svc_act = build_service("driveactivity", "v2", profile)
        p.add_argument("--item-name")
        p.add_argument("--ancestor-name")
        p.add_argument("--max", type=int, default=10)
        a = p.parse_args(args)
        activity(svc_act, a.item_name, a.ancestor_name, a.max)

    else:
        _err(f"Unknown drive command: {command}")
