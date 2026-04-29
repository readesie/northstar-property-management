"""
lease_index.py
NorthStar Property Management

Lease document index — tracks where every lease file lives,
renewal status, and key terms. Kills the "where did I save that?" problem.
"""

import json
from datetime import date, datetime
from pathlib import Path
from dataclasses import dataclass, field, asdict
from typing import Optional

DATA_FILE = Path(__file__).parent.parent.parent / "data" / "leases.json"


@dataclass
class LeaseRecord:
    lease_id: str
    tenant_id: str
    tenant_name: str
    property_address: str
    unit: str
    lease_start: str          # ISO date
    lease_end: str            # ISO date
    monthly_rent: float
    security_deposit: float
    document_path: str = ""   # Path to the actual PDF/docx lease file
    renewal_status: str = "none"   # none | offered | signed | declined
    rent_increase_clause: bool = False
    pet_allowed: bool = False
    notes: str = ""


def load_leases() -> list[LeaseRecord]:
    if not DATA_FILE.exists():
        return []
    with open(DATA_FILE) as f:
        raw = json.load(f)
    return [LeaseRecord(**r) for r in raw]


def save_leases(leases: list[LeaseRecord]) -> None:
    DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(DATA_FILE, "w") as f:
        json.dump([asdict(r) for r in leases], f, indent=2)


def add_lease(record: LeaseRecord) -> None:
    leases = load_leases()
    leases.append(record)
    save_leases(leases)
    print(f"✅ Lease {record.lease_id} indexed for {record.tenant_name}")


def get_active_leases() -> list[LeaseRecord]:
    today = date.today()
    return [
        r for r in load_leases()
        if date.fromisoformat(r.lease_end) >= today
    ]


def get_lease_summary() -> str:
    leases = get_active_leases()
    if not leases:
        return "No active leases indexed."
    today = date.today()
    lines = ["LEASE INDEX", "=" * 50]
    for r in sorted(leases, key=lambda x: x.lease_end):
        days = (date.fromisoformat(r.lease_end) - today).days
        flag = " ⚠️" if days <= 60 else ""
        doc = r.document_path if r.document_path else "⚠️  No document path"
        lines.append(
            f"\n{r.tenant_name} @ {r.property_address} {r.unit}\n"
            f"  Lease: {r.lease_start} → {r.lease_end} ({days} days){flag}\n"
            f"  Rent: ${r.monthly_rent:,.2f} | Deposit: ${r.security_deposit:,.2f}\n"
            f"  Renewal: {r.renewal_status}\n"
            f"  Doc: {doc}"
        )
    return "\n".join(lines)
