"""
Client service — lookup, create, and update clients in Airtable.
Returns dicts with the same shape the rest of the app expects:
  { "id", "email", "first_name", "last_name", "phone", "metadata" }
"""
from typing import Optional, Dict, Any
from pyairtable.formulas import match
from app.services.airtable_client import clients_table


# Map lowercase urgency values → Airtable select options
_URGENCY_MAP = {
    "low": "Low",
    "medium": "Normal",
    "normal": "Normal",
    "high": "High",
    "urgent": "Urgent",
}


def _normalize_urgency(value: str) -> str:
    """Convert any urgency string to the exact Airtable option."""
    return _URGENCY_MAP.get(str(value).strip().lower(), "Normal")


def _record_to_dict(rec: Dict[str, Any]) -> Dict[str, Any]:
    f = rec.get("fields", {})
    name = f.get("Name") or ""
    first, _, last = name.partition(" ")
    return {
        "id": rec["id"],
        "email": f.get("Email"),
        "phone": f.get("Phone"),
        "first_name": first or None,
        "last_name": last or None,
        "intake_type": f.get("Intake Type"),
        "situation": f.get("Situation"),
        "urgency": f.get("Urgency"),
        "status": f.get("Status"),
        "channel": f.get("Channel"),
        "metadata": {
            "intake_type": f.get("Intake Type"),
            "situation": f.get("Situation"),
            "urgency": f.get("Urgency"),
            "notes": f.get("Notes"),
        },
    }


async def lookup_by_email(email: str) -> Optional[Dict[str, Any]]:
    if not email:
        return None
    tbl = clients_table()
    rec = tbl.first(formula=match({"Email": email}))
    return _record_to_dict(rec) if rec else None


async def lookup_by_phone(phone: str) -> Optional[Dict[str, Any]]:
    """Lookup client by phone number (fallback when no email)."""
    if not phone:
        return None
    tbl = clients_table()
    # Strip non-digits for flexible matching
    digits = "".join(c for c in phone if c.isdigit())
    rec = tbl.first(formula=match({"Phone": phone}))
    return _record_to_dict(rec) if rec else None


async def create_client(
    email: str = "",
    first_name: Optional[str] = None,
    last_name: Optional[str] = None,
    phone: Optional[str] = None,
    channel: str = "Chatbot",
) -> Dict[str, Any]:
    fields: Dict[str, Any] = {"Channel": channel, "Status": "New", "Source": "Chatbot"}
    if email:
        fields["Email"] = email
    name_parts = [p for p in (first_name, last_name) if p]
    if name_parts:
        fields["Name"] = " ".join(name_parts)
    if phone:
        fields["Phone"] = phone
    rec = clients_table().create(fields, typecast=True)
    return _record_to_dict(rec)


async def update_client(client_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
    """
    Accepts the flat update dict used by save_client tool:
    keys like first_name, last_name, phone, email, metadata (dict).
    Converts them to Airtable field names.
    """
    fields: Dict[str, Any] = {}
    first = updates.get("first_name")
    last = updates.get("last_name")
    if first or last:
        fields["Name"] = " ".join(p for p in (first, last) if p)
    if updates.get("email"):
        fields["Email"] = updates["email"]
    if updates.get("phone"):
        fields["Phone"] = updates["phone"]
    meta = updates.get("metadata") or {}
    if meta.get("intake_type"):
        fields["Intake Type"] = meta["intake_type"]
    if meta.get("situation") or meta.get("situation_summary"):
        fields["Situation"] = meta.get("situation") or meta.get("situation_summary")
    if meta.get("urgency"):
        fields["Urgency"] = _normalize_urgency(meta["urgency"])
    if meta.get("notes"):
        fields["Notes"] = meta["notes"]
    # Update status to Lead when contact info arrives
    if updates.get("phone") or updates.get("email"):
        fields.setdefault("Status", "New Lead")

    if not fields:
        return {}

    rec = clients_table().update(client_id, fields, typecast=True)
    return _record_to_dict(rec)


async def get_or_create_client(
    email: str = "",
    first_name: Optional[str] = None,
    last_name: Optional[str] = None,
    phone: Optional[str] = None,
    channel: str = "Chatbot",
) -> tuple[Dict[str, Any], bool]:
    # Try email first, then phone
    existing = None
    if email:
        existing = await lookup_by_email(email)
    if not existing and phone:
        existing = await lookup_by_phone(phone)
    if existing:
        return existing, False
    new_client = await create_client(email, first_name, last_name, phone, channel)
    return new_client, True
