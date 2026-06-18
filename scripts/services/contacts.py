import argparse

from core import _out, _err, build_service


# ─── Operations ──────────────────────────────────────────────────────────────

def list_contacts(svc, max_results: int = 20) -> None:
    resp = svc.people().connections().list(
        resourceName="people/me",
        pageSize=max_results,
        personFields="names,emailAddresses,phoneNumbers",
    ).execute()
    _out([
        {
            "name": p.get("names", [{}])[0].get("displayName", "") if p.get("names") else "",
            "emails": [e["value"] for e in p.get("emailAddresses", [])],
            "phones": [ph["value"] for ph in p.get("phoneNumbers", [])],
        }
        for p in resp.get("connections", [])
    ])


def list_groups(svc) -> None:
    resp = svc.contactGroups().list().execute()
    _out([
        {
            "id": g.get("resourceName"),
            "name": g.get("name", ""),
            "memberCount": g.get("memberCount", 0),
            "type": g.get("groupType", ""),
        }
        for g in resp.get("contactGroups", [])
    ])


def list_group(svc, group_id: str) -> None:
    resp = svc.contactGroups().get(resourceName=group_id, maxMembers=500).execute()
    member_resource_names = resp.get("memberResourceNames", [])
    if not member_resource_names:
        _out([])
        return
    people_resp = svc.people().getBatchGet(
        resourceNames=member_resource_names,
        personFields="names,emailAddresses",
    ).execute()
    _out([
        {
            "name": person.get("names", [{}])[0].get("displayName", "") if person.get("names") else "",
            "emails": [e["value"] for e in person.get("emailAddresses", [])],
        }
        for entry in people_resp.get("responses", [])
        for person in [entry.get("person", {})]
    ])


def search(svc, query: str) -> None:
    resp = svc.people().searchContacts(
        query=query,
        readMask="names,emailAddresses,phoneNumbers",
    ).execute()
    _out([
        {
            "name": person.get("names", [{}])[0].get("displayName", "") if person.get("names") else "",
            "emails": [e["value"] for e in person.get("emailAddresses", [])],
            "phones": [ph["value"] for ph in person.get("phoneNumbers", [])],
        }
        for result in resp.get("results", [])
        for person in [result.get("person", {})]
    ])


# ─── Dispatch ─────────────────────────────────────────────────────────────────

def dispatch(profile: str, command: str, args: list) -> None:
    svc = build_service("people", "v1", profile)
    p = argparse.ArgumentParser(prog=f"contacts {command}")

    if command == "list":
        p.add_argument("--max", type=int, default=20)
        a = p.parse_args(args)
        list_contacts(svc, a.max)

    elif command == "list-groups":
        list_groups(svc)

    elif command == "list-group":
        p.add_argument("group_id")
        a = p.parse_args(args)
        list_group(svc, a.group_id)

    elif command == "search":
        p.add_argument("query")
        a = p.parse_args(args)
        search(svc, a.query)

    else:
        _err(f"Unknown contacts command: {command}")
