"""
tenant_registry.py
NorthStar Property Management

Tenant contact sheet, lease tracking, and alert generation.
Pain it kills: chasing people via text, forgetting who lives where,
missing lease expirations until it's too late.
"""

import csv
import json
from datetime import date, datetime, timedelta
from pathlib import Path
from dataclasses import dataclass, field, asdict
from typing import Optional
import sys
sys.path.append(str(Path(__file__).parent.parent))
from utils.notifier import send_alert


DATA_FILE = Path(__file__).parent.parent.parent / "data" / "tenants.json"

LEASE_WARN_DAYS = [90, 60, 30, 14]  # Days before expiry to send warnings


@dataclass
class Tenant:
    tenant_id: str
    name: str
    property_address: str
    unit: str
    phone: str
    email: str
    lease_start: str          # ISO date string
    lease_end: str            # ISO date string
    monthly_rent: float
    security_deposit: float
    status: str = "active"    # active | notice | vacated
    notes: str = ""
    emergency_contact_name: str = ""
    emergency_contact_phone: str = ""


def load_tenants() -> list[Tenant]:
    if not DATA_FILE.exists():
        return []
    with open(DATA_FILE) as f:
        raw = json.load(f)
    return [Tenant(**t) for t in raw]


def save_tenants(tenants: list[Tenant]) -> None:
    DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(DATA_FILE, "w") as f:
        json.dump([asdict(t) for t in tenants], f, indent=2)


def add_tenant(tenant: Tenant) -> None:
    tenants = load_tenants()
    if any(t.tenant_id == tenant.tenant_id for t in tenants):
        raise ValueError(f"Tenant ID {tenant.tenant_id} already exists.")
    tenants.append(tenant)
    save_tenants(tenants)
    print(f"✅ Added tenant: {tenant.name} @ {tenant.property_address} {tenant.unit}")


def check_lease_expirations(dry_run: bool = False) -> list[dict]:
    """
    Check all active leases for upcoming expiration.
    Sends alerts at 90/60/30/14 days out.
    Returns list of alert dicts for logging.
    """
    tenants = load_tenants()
    today = date.today()
    alerts_fired = []

    for t in tenants:
        if t.status != "active":
            continue
        lease_end = date.fromisoformat(t.lease_end)
        days_left = (lease_end - today).days

        for warn_day in LEASE_WARN_DAYS:
            if days_left == warn_day:
                msg = (
                    f"LEASE EXPIRATION ALERT\n"
                    f"Tenant: {t.name}\n"
                    f"Property: {t.property_address} {t.unit}\n"
                    f"Lease ends: {t.lease_end} ({days_left} days)\n"
                    f"Contact: {t.phone} | {t.email}\n"
                    f"Monthly rent: ${t.monthly_rent:,.2f}\n"
                    f"\nAction needed: Begin renewal conversation or send non-renewal notice."
                )
                alert = {
                    "type": "lease_expiration",
                    "tenant_id": t.tenant_id,
                    "tenant_name": t.name,
                    "property": t.property_address,
                    "days_left": days_left,
                    "lease_end": t.lease_end,
                    "message": msg,
                }
                alerts_fired.append(alert)
                if not dry_run:
                    send_alert(
                        subject=f"⚠️ Lease expiring in {days_left} days — {t.name}",
                        body=msg
                    )
                break  # Only fire one threshold per day per tenant

    return alerts_fired


def check_rent_due(dry_run: bool = False) -> list[dict]:
    """
    Simple rent due reminder: fires on the 28th (3-day heads up for 1st),
    the 1st, and the 4th (3 days past due).
    """
    tenants = load_tenants()
    today = date.today()
    day = today.day
    alerts_fired = []

    if day not in (28, 1, 4):
        return []

    for t in tenants:
        if t.status != "active":
            continue

        if day == 28:
            subject = f"💰 Rent reminder: ${t.monthly_rent:,.0f} due in 3 days — {t.name}"
            body = (
                f"Hi {t.name.split()[0]},\n\n"
                f"Just a friendly reminder that your rent of ${t.monthly_rent:,.2f} "
                f"is due on the 1st.\n\n"
                f"Property: {t.property_address} {t.unit}\n\n"
                f"Thank you!"
            )
        elif day == 1:
            subject = f"💰 Rent due today — {t.name}"
            body = (
                f"Hi {t.name.split()[0]},\n\n"
                f"Your rent of ${t.monthly_rent:,.2f} is due today.\n\n"
                f"Property: {t.property_address} {t.unit}\n\n"
                f"Thank you!"
            )
        else:  # day == 4
            subject = f"🔴 Rent overdue — {t.name} — ${t.monthly_rent:,.0f}"
            body = (
                f"OWNER ALERT — Rent appears overdue.\n\n"
                f"Tenant: {t.name}\n"
                f"Property: {t.property_address} {t.unit}\n"
                f"Amount: ${t.monthly_rent:,.2f}\n"
                f"Contact: {t.phone} | {t.email}\n"
                f"Due: {today.replace(day=1).isoformat()}\n\n"
                f"No payment confirmation on file. Follow up today."
            )

        alert = {
            "type": "rent_due",
            "tenant_id": t.tenant_id,
            "tenant_name": t.name,
            "day_of_month": day,
            "amount": t.monthly_rent,
        }
        alerts_fired.append(alert)

        if not dry_run:
            # Send to tenant on 28th/1st, to owner on 4th
            recipient = t.email if day in (28, 1) else None
            send_alert(subject=subject, body=body, to=recipient)

    return alerts_fired


def get_tenant_summary() -> str:
    """Return a plain-text summary of all active tenants — owner-facing."""
    tenants = [t for t in load_tenants() if t.status == "active"]
    if not tenants:
        return "No active tenants on record."

    today = date.today()
    lines = [f"ACTIVE TENANTS — {today.isoformat()}", "=" * 50]
    total_rent = 0.0

    for t in tenants:
        lease_end = date.fromisoformat(t.lease_end)
        days_left = (lease_end - today).days
        flag = " ⚠️" if days_left <= 60 else ""
        lines.append(
            f"\n{t.name}\n"
            f"  {t.property_address} {t.unit}\n"
            f"  📞 {t.phone}  ✉️  {t.email}\n"
            f"  Rent: ${t.monthly_rent:,.2f}/mo\n"
            f"  Lease: {t.lease_start} → {t.lease_end} ({days_left} days left){flag}"
        )
        total_rent += t.monthly_rent

    lines.append(f"\n{'=' * 50}")
    lines.append(f"Total monthly rent roll: ${total_rent:,.2f}")
    return "\n".join(lines)


if __name__ == "__main__":
    print(get_tenant_summary())
